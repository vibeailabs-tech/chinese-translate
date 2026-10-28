# translate-zh-highlight

An AI agent skill that translates prose into **Simplified Chinese** and exports a polished **Word (`.docx`) reading document** with every proper name highlighted in yellow.

Works with agents that support the `SKILL.md` format, such as [Devin](https://devin.ai), Claude Code, and OpenAI Codex.

> Tiếng Việt: Skill dịch văn bản sang tiếng Trung giản thể và xuất ra file Word đã định dạng sẵn. Tất cả tên riêng được tô vàng, tên tiếng Anh giữ nguyên.

---

## Features

- **Faithful translation**: keeps meaning, tone, paragraph order, numbers, dates, and units. No summarizing and no added facts.
- **Proper-name handling**
  - Proper names are identified from context (people, places, organizations, brands, events), not just from capital letters.
  - English proper names stay exactly as written (`New York` stays `New York`).
  - Vietnamese personal names keep their diacritics (`Nguyễn Văn An`). Places with a well-established Chinese name are translated (`Hà Nội` → `河内`).
  - Each name is translated the same way every time. A glossary you provide overrides these defaults.
- **Yellow highlighting** on every proper-name occurrence, including in the title, the subtitle, and the running header.
- **Consistent Word layout** taken from a bundled template:
  - US Letter, portrait, 1-inch margins
  - **Hiragino Sans GB, 13 pt** throughout
  - Centered opening block: reading label, title, subtitle, and a highlighting legend
  - Justified body, 26 pt first-line indent, 8 pt paragraph spacing, ~1.33 line spacing
  - Running header showing the document title, plus a page-number footer
- **Safe output**: a new file is named after the translated title. Existing files are never overwritten (a numbered suffix such as `标题 (2).docx` is used instead).

## Example output

Input:

> John Smith met Nguyễn Văn An in Hà Nội.

Output document body (highlighted segments shown in **bold** here):

> **John Smith**在**河内**与**Nguyễn Văn An**会面。

---

## Repository layout

```
.
├── translate-zh-highlight/          # The skill package (copy this folder to install)
│   ├── SKILL.md                     # Instructions the agent follows
│   ├── agents/openai.yaml           # Display metadata for OpenAI/Codex agents
│   ├── assets/document-template/    # Unpacked Word XML template (layout source of truth)
│   └── scripts/export_docx.py       # JSON → .docx exporter
└── .devin/skills/translate-zh-highlight/   # Same skill, so Devin picks it up when this repo is opened as a project
```

## Requirements

- Python 3.9+
- [`lxml`](https://pypi.org/project/lxml/)
- The **Hiragino Sans GB** font for exact on-screen appearance. It ships with macOS. On other systems Word substitutes another font, because the font is set in the document but not embedded.

```bash
python3 -m pip install lxml
```

## Installation

Clone the repository:

```bash
git clone https://github.com/vibeailabs-tech/chinese-translate.git
```

Then copy the `translate-zh-highlight/` folder into your agent's skills directory:

| Agent | Project-level | User-level (global) |
|-------|---------------|---------------------|
| Devin | `<project>/.devin/skills/` | `~/.config/devin/skills/` |
| Claude Code | `<project>/.claude/skills/` | `~/.claude/skills/` |
| OpenAI Codex | — | `~/.codex/skills/` |

For example, to install globally for Devin:

```bash
mkdir -p ~/.config/devin/skills
cp -R chinese-translate/translate-zh-highlight ~/.config/devin/skills/
```

## Usage

Ask your agent to translate something into Chinese. The skill triggers automatically, or you can invoke it by name:

```
Translate this article into Simplified Chinese with names highlighted:

<paste text here>
```

The agent will:

1. Translate the text and build an internal proper-name mapping.
2. Write a short Chinese title and subtitle for the document.
3. Export the `.docx` using the bundled template.
4. Check the document for omissions, highlights, fonts, margins, and layout.
5. Save the final `.docx` in your current working directory and give you a link to it.

You can also supply a glossary, for example: "keep `Đà Nẵng` as `岘港`, keep `VinGroup` in English".

---

## Using the exporter directly

The exporter can be used without an agent. Its input is a UTF-8 JSON file with exactly three keys:

| Key | Type | Description |
|-----|------|-------------|
| `title` | array of segments | Document title (required, non-empty) |
| `subtitle` | array of segments | Subtitle (required, non-empty) |
| `paragraphs` | array of arrays of segments | Body paragraphs. An empty array produces a blank paragraph. |

Each segment is `{"text": "...", "highlight": true|false}`. `highlight` is optional and defaults to `false`. Inside `text`, `\n` becomes a line break and `\t` becomes a tab. The exporter does not add spaces between segments.

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

Run:

```bash
python3 translate-zh-highlight/scripts/export_docx.py translation.json 一次会面.docx
```

Behavior:

- The output path must end in `.docx`.
- The exporter **refuses to overwrite** an existing file and exits with `File exists`.
- Unknown keys, a missing title or subtitle, non-boolean `highlight` values, and invalid XML characters are rejected with an error.
- The file is built fully in memory before it is written, so a failed run never leaves a partial file behind.
- The page-number field is marked for refresh, so Word updates it when the file is opened.

> The exporter only handles formatting. It does not translate text, find proper names, or judge translation quality; the agent does that work.

## Limitations

- Only plain paragraphs are supported. Tables, lists, and footnotes in the source are not handled by the exporter; the skill tells the agent to extend the template rather than silently flatten them.
- The Hiragino Sans GB font is not embedded. Documents opened on machines without the font will look different.
- The opening label is always `简体中文读本`. No HSK level or vocabulary exercises are added.

## Customization

- **Font and size**: edit `FONT` and the `sz` value (half-points, `26` = 13 pt) in `scripts/export_docx.py`.
- **Layout and colors**: edit the XML in `assets/document-template/word/` (`document.xml`, `styles.xml`, `header1.xml`, `footer1.xml`).
- **Translation rules**: edit `SKILL.md`.

If you change the skill, update both copies (`translate-zh-highlight/` and `.devin/skills/translate-zh-highlight/`) so they stay in sync.

## License

No license has been specified yet. All rights are reserved by the author until a license is added.
