# Learning Machine Official Website

Static website for [learning-machine.ai](https://learning-machine.ai).

The site is published with GitHub Pages from the `main` branch.

## Public pages

- Multilingual home and careers pages are available in English, Simplified Chinese, French, and German.
- English policy pages live at `/privacy/`, `/applicant-privacy/`, and `/terms/`.
- Policy links from localized home and careers pages preserve the selected site language.

## Validate legal pages

Run the same link, content, and generator checks used by CI:

```bash
node tests/check-legal-pages.mjs
```
