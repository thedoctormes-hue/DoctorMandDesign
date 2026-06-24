# DoctorMandDesign

Генератор презентаций для лаборатории LabDoctorM.

## Быстрый старт

```bash
cd /root/LabDoctorM/projects/DoctorMandDesign
python3 generate.py
# Результат: output/slides.pdf
```

## Структура

```
DoctorMandDesign/
├── design-system.css    # CSS-переменные и компоненты
├── slides.html          # Jinja2 шаблон презентации
├── generate.py          # Генератор PDF (WeasyPrint)
├── test_generate.py     # Тесты
└── output/              # Сгенерированные файлы
```

## Зависимости

- weasyprint >= 69.0
- jinja2 >= 3.0
- poppler-utils (pdftoppm для скриншотов)

## Дизайн-система

Основана на референсе polyscop.shtab-ai.ru:
- Фон: #040A14
- Акцент: #00E5FF
- Текст: #E6F1FF
- Формат: 16:9 (256mm × 144mm)

## Тестирование

```bash
python3 test_generate.py
```

## Автор

Сова (owl) — LabDoctorM, 2026-06-24
