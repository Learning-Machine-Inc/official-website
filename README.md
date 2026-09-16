# Learning Machine Official Website

Static website for [learning-machine.ai](https://learning-machine.ai).

The site is published with GitHub Pages from the `main` branch.

## Public pages

- Multilingual home and careers pages are available in English, Simplified Chinese, French, and German.
- English legal pages live at `/privacy/`, `/applicant-privacy/`, `/terms/`, and `/legal/`.

## Validate legal pages

Run the same link, content, and generator checks used by CI:

```bash
node tests/check-legal-pages.mjs
```
