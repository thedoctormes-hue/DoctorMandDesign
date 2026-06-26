# Changelog

All notable changes to DoctorMandDesign will be documented in this file.

## [1.1.0] - 2026-06-24

### Added
- 13 new slide template variants (hero-split, hero-minimal, hero-bold, problem-split, solution-minimal, stats-big, roadmap-timeline, team-grid, comparison-cards, faq-accordion, cta-bold)
- WCAG-AA contrast verification for all 17 base + variant combinations
- i18n support (RU/EN) with localized section labels and page numbers
- AI-prompt flag (--prompt) for base presentation generation from text
- Auto-publish script (scripts/publish_to_yandex.sh) — uploads PDF to Yandex Disk + Telegram notification
- CI pipeline updated with colour-science, tesseract-ocr, release PDF generation and publishing steps

### Changed
- Template architecture refactored to modular system (18 base templates in templates/slides/)
- Design system expanded with utility classes in design-system.css
- verify.py updated with precise contrast calculation via colour-science

## [1.0.0] - 2026-06-24

### Added
- Initial release: 18 modular slide templates
- WeasyPrint + Jinja2 + CSS Grid rendering
- Design system based on Polyscope reference (#040A14, #00E5FF, #E6F1FF)
- Presentation types: Scopiq (RU/EN), Lab Profile (RU/EN)
- Roadmap (5 phases)
