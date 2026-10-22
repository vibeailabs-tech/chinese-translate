#!/usr/bin/env python3
"""Export a translation using the bundled Word template."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED

FONT = 'Hiragino Sans GB'
TEMPLATE = Path(__file__).resolve().parents[1] / 'assets' / 'document-template'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def validate(data):
    if not isinstance(data, dict) or set(data) != {'title', 'subtitle', 'paragraphs'}:
        raise ValueError("Input requires exactly title, subtitle, and paragraphs.")
    if not isinstance(data['paragraphs'], list) or not data['paragraphs']:
        raise ValueError('paragraphs must be a nonempty array.')
    for label, segments in [('title', data['title']), ('subtitle', data['subtitle'])] + [
        (f'paragraph {i+1}', p) for i, p in enumerate(data['paragraphs'])
    ]:
        if not isinstance(segments, list):
            raise ValueError(f'{label} must be an array of segments.')
        for segment in segments:
            if not isinstance(segment, dict) or not set(segment) <= {'text', 'highlight'}:
                raise ValueError(f'Invalid segment in {label}.')
            if not isinstance(segment.get('text'), str):
                raise ValueError('Each segment needs a string text.')
            if type(segment.get('highlight', False)) is not bool:
                raise ValueError('highlight must be a JSON boolean.')
            if any(not (c in '\t\n\r' or 32 <= ord(c) <= 0xD7FF or 0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF) for c in segment['text']):
                raise ValueError('Text contains an unsupported XML character.')
        if label in ('title', 'subtitle') and not any(s['text'].strip() for s in segments):
            raise ValueError(f'{label} must contain text.')
    if not any(s['text'].strip() for p in data['paragraphs'] for s in p):
        raise ValueError('The translation must contain text.')
    return data


def export(data, output):
    from lxml import etree as E
    data = validate(data)
    output = Path(output)
    if output.suffix.lower() != '.docx':
        raise ValueError('Output must use the .docx extension.')
    if not (TEMPLATE / 'word/document.xml').is_file():
        raise ValueError(f'Missing required template: {TEMPLATE}. Do not use a generic layout.')
    def q(tag): return '{' + W + '}' + tag
    def child(el, tag):
        node = el.find(q(tag))
        if node is None: node = E.SubElement(el, q(tag))
        return node
    def font(run):
        rp = run.find(q('rPr'))
        if rp is None:
            rp = E.Element(q('rPr')); run.insert(0, rp)
        rf = child(rp, 'rFonts'); rf.attrib.clear()
        for key in ('ascii', 'hAnsi', 'eastAsia', 'cs'): rf.set(q(key), FONT)
        for key in ('sz', 'szCs'): child(rp, key).set(q('val'), '26')
        return rp
    def paragraph(template, segments, centered=False, body=False):
        p = deepcopy(template); p.attrib.clear()
        for c in list(p):
            if c.tag != q('pPr'): p.remove(c)
        if centered:
            child(child(p, 'pPr'), 'ind').set(q('firstLine'), '0')
        if body:
            pp = child(p, 'pPr')
            child(pp, 'jc').set(q('val'), 'both')
            child(pp, 'ind').set(q('firstLine'), '520')
            spacing = child(pp, 'spacing')
            spacing.set(q('after'), '160')
            spacing.set(q('line'), '320')
            spacing.set(q('lineRule'), 'auto')
            child(pp, 'widowControl')
        for segment in segments:
            r = E.SubElement(p, q('r')); rp = font(r)
            if segment.get('highlight', False): child(rp, 'highlight').set(q('val'), 'yellow')
            # Word represents tabs and line breaks as elements, not text characters.
            text = segment['text'].replace('\r\n', '\n').replace('\r', '\n')
            for i, line in enumerate(text.split('\n')):
                if i: E.SubElement(r, q('br'))
                for j, chunk in enumerate(line.split('\t')):
                    if j: E.SubElement(r, q('tab'))
                    t = E.SubElement(r, q('t'))
                    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); t.text = chunk
        return p
    def xml(el): return E.tostring(el, encoding='UTF-8', xml_declaration=True, standalone=True)
    parts = {p.relative_to(TEMPLATE).as_posix(): p.read_bytes()
             for p in sorted(TEMPLATE.rglob('*')) if p.is_file()}
    document = E.fromstring(parts['word/document.xml']); body = document.find(q('body'))
    patterns = body.findall(q('p')); section = deepcopy(body.find(q('sectPr')))
    if len(patterns) < 5: raise ValueError('Template lacks the expected opening and body patterns.')
    for node in list(body): body.remove(node)
    opening = [
        [{'text': '简体中文读本'}], data['title'], data['subtitle'],
        [{'text': '标记说明：黄色标出专有名称；英文专名保留原文。'}],
    ]
    for pattern, segments in zip(patterns[:4], opening): body.append(paragraph(pattern, segments, True))
    for segments in data['paragraphs']: body.append(paragraph(patterns[4], segments, body=True))
    body.append(section); parts['word/document.xml'] = xml(document)
    header = E.fromstring(parts['word/header1.xml']); old = header.find(q('p'))
    new = paragraph(old, data['title'])
    for run in new.findall(q('r')): child(font(run), 'color').set(q('val'), '707070')
    header.replace(old, new); parts['word/header1.xml'] = xml(header)
    footer = E.fromstring(parts['word/footer1.xml'])
    for run in footer.iter(q('r')): font(run)
    for field in footer.iter(q('fldChar')):
        if field.get(q('fldCharType')) == 'begin': field.set(q('dirty'), 'true')
    parts['word/footer1.xml'] = xml(footer)
    settings = E.fromstring(parts['word/settings.xml'])
    child(settings, 'updateFields').set(q('val'), 'true'); parts['word/settings.xml'] = xml(settings)
    # Build fully in memory before exclusive creation to avoid partial output.
    from io import BytesIO
    buffer = BytesIO()
    with ZipFile(buffer, 'w', ZIP_DEFLATED) as z:
        for name, value in parts.items(): z.writestr(name, value)
    with output.open('xb') as stream: stream.write(buffer.getvalue())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        export(json.loads(args.input.read_text(encoding='utf-8')), args.output)
    except ImportError:
        print('Error: install lxml in a task-local virtual environment.', file=sys.stderr)
        return 1
    except (ValueError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    print(args.output.resolve())
    return 0


if __name__ == '__main__':
    sys.exit(main())
