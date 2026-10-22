---
name: translate-zh-highlight
description: Translate prose into Simplified Chinese and export a Word document in the bundled document layout with proper names highlighted yellow, English proper names preserved, Hiragino Sans GB 13 pt, and one-inch margins. Use for translation documents with these formatting requirements, not vocabulary lessons or stories.
---

# Translate to Simplified Chinese

Every output must use the bundled [document template](assets/document-template/word/document.xml). Deliver a `.docx` with its opening block, running header, page-number footer, and translated body. Do not add a separate cover, glossary, source text, or translator notes unless requested. `.docx` is the default Word format; never disguise it with a `.doc` extension.

## Translation and names

- Translate faithfully into natural Simplified Chinese. Preserve meaning, tone, paragraph order, numbers, dates, and units; do not summarize or add facts.
- Identify proper names in context: people, places, organizations, brands, and named institutions or events. Capitalization alone does not establish a proper name (Apple the company versus an apple).
- Preserve English proper names exactly, including capitalization, spelling, and internal punctuation, even when a conventional Chinese translation exists: `New York` stays `New York`.
- Default for Vietnamese names: preserve personal names with diacritics; translate places with a well-established Chinese name (`Hà Nội` → `河内`). For other non-English names, use a confidently known conventional Chinese form; otherwise preserve the original rather than inventing a transliteration. User glossaries override these defaults.
- Build a small internal name mapping before translating and use it consistently. If a material ambiguity cannot be resolved from context, ask a focused question; otherwise preserve the uncertain name and briefly mention uncertainty outside the document.
- Highlight every proper-name occurrence in the final translation with yellow background, including preserved names. Highlight the name span only, excluding surrounding whitespace, punctuation, titles, or generic nouns unless they belong to the name. Do not highlight pronouns or generic references merely because they refer to a named entity.

## Required layout

Use `assets/document-template/` as the layout authority for **every output**. The template is stored as unpacked Word XML parts preserving the approved layout. The exporter assembles these parts into a Word document and replaces the content; do not create a blank document or fall back to a generic layout. The bundled template makes the skill independent of the original file location.

- Letter portrait, four 1-inch margins, header/footer distance 708 twips.
- Centered opening: blue bold reading label, dark-blue bold title, gray italic subtitle, gray highlighting legend. Write a short, accurate topic title and subtitle; apply name highlighting there and in the running header too.
- Body: justified, first-line indent 26 pt, 8 pt after paragraphs, proportional line spacing 320/240 (about 1.33), widow control.
- Running header: topic title aligned left. Footer: page number aligned right, refreshed by Word when opened.
- Explicit user typography overrides template size differences: **Hiragino Sans GB, 13 pt throughout**, including opening, header, and footer. Keep template colors and emphasis.
- The reference's sample content, HSK 6 label, vocabulary-level claims, and vocabulary underlining are not part of the translation task. Use the neutral label `简体中文读本`; do not claim an HSK level or introduce vocabulary exercises.
- If the template is missing or damaged, report the blocker rather than silently changing the form.

## Output location

Save the completed deliverable in `output/` inside this skill folder. Resolve the skill folder from the active `SKILL.md` path, create its `output/` directory if needed. Never place final deliverables in the active project's top-level `output/`, on the Desktop, or in the skill installation parent directory. Keep temporary JSON, provisional DOCX files, rendering previews, and QA files in a temporary directory.

**Preserve previous deliverables:** never delete, overwrite, or rename an existing file in `output/` when creating a new translation. Each run adds one verified `.docx`; the directory may contain multiple deliverables. Name the new file from the translated document title, preserving meaningful words and using the title's original script. Replace filesystem-reserved characters with hyphens, trim surrounding spaces and dots, and append `.docx`; do not use a generic name such as `translation-zh.docx`. If that filename already exists, append the smallest available numbered suffix before `.docx` (for example, `标题 (2).docx`). After verification, transfer the staging file with a method that refuses to replace an existing destination, confirm the new file exists, and link to that exact file. Never clean old `.docx` files as part of this workflow.

## Export

Create UTF-8 JSON in a temporary working directory. The required `title` and `subtitle` fields and each body paragraph are ordered arrays of text segments. Explicitly mark name segments; omitted `highlight` means false. Empty arrays preserve blank paragraphs. Do not add spaces merely to separate segments.

```json
{
  "title": [{"text": "一次会面"}],
  "subtitle": [{"text": "会面地点与参与者"}],
  "paragraphs": [
    [
      {"text": "John Smith", "highlight": true},
      {"text": "在"},
      {"text": "河内", "highlight": true},
      {"text": "与"},
      {"text": "Nguyễn Văn An", "highlight": true},
      {"text": "会面。"}
    ]
  ]
}
```

Run the bundled exporter using paths resolved relative to this skill folder, with a temporary DOCX destination:

```bash
python3 scripts/export_docx.py /absolute/path/translation.json /temporary/path/translation-zh.docx
```

Requires `lxml`. If unavailable, install it in a task-local virtual environment and run with that interpreter. The exporter always uses the bundled document template and refuses to replace existing files; use a temporary staging directory because it refuses to replace existing files. Unknown JSON keys and missing title/subtitle are rejected.

The exporter handles paragraphs, not complex source layouts. If a source has tables, lists, or footnotes that must be retained, use an available document workflow to preserve that structure by extending the bundled template while applying the same typography, paragraph layout, header/footer, margins, and name highlights; do not silently flatten it.

## Verify and deliver

1. Compare the full translation against the source for omissions, numbers, and meaning. Check the internal name mapping against every occurrence, including names in headings.
2. Reopen the DOCX and check the text, yellow highlights, 13 pt font settings (including East Asian font), and all four margins. Also verify the four-part opening, Letter page size, justified body, 26 pt first-line indent, 8 pt paragraph spacing, running header, and PAGE field. Confirm no sample body text or unsupported HSK claims remain. The exporter does not identify names or assess translation quality.
3. When a document renderer is available, render and inspect every page for missing glyphs, wrapping, and clipping. If unavailable, report the visual verification limitation briefly. Setting a font in DOCX does not install or embed it; never silently substitute another font or claim exact appearance without verification.
4. Return a link to the final `.docx`. Keep intermediate JSON and QA artifacts out of the delivery unless requested.
