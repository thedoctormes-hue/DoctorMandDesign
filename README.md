# DoctorMandDesign

Генератор презентаций для лаборатории LabDoctorM.

## Быстрый старт

```bash
cd /root/LabDoctorM/projects/DoctorMandDesign
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Шрифты уже скачаны (Inter, Oswald) и находятся в assets/fonts/
#    Если нужно переустановить шрифты, запустите:
#    ./setup_fonts.sh

# 3. Подготовьте JSON-данные (пример – example-data.json или example-data.en.json)
python3 generate.py --data example-data.json --output output/demo.pdf
```

### English mode

```bash
cd /root/LabDoctorM/projects/DoctorMandDesign
python3 generate.py --data example-data.en.json --output output/poliscop_en.pdf
```
The same design system is used, only the textual content switches to English.

## Проверка качества
```bash
python3 verify.py output/demo.pdf > output/verify_report.json
cat output/verify_report.json
```

## Тесты
```bash
pytest -q
```

## Структура

```
DoctorMandDesign/
├── design-system.css        # CSS-переменные и компоненты
├── template.j2              # Главный Jinja2-шаблон (цикл по слайдам + include)
├── generate.py              # Генератор PDF (WeasyPrint) с поддержкой JSON→Jinja2
├── verify.py                # Проверка качества сгенерированного PDF (OCR + контраст)
├── example-data.json        # Пример данных на русском
├── example-data.en.json     # Пример данных на английском
├── requirements.txt         # Зависимости Python
├── test_generate.py         # Тесты
├── templates/
│   ├── base.j2              # Базовый layout (HTML head + body)
│   └── slides/              # Модульные шаблоны слайдов
│       ├── hero.j2
│       ├── problem.j2
│       ├── solution.j2
│       ├── how.j2
│       ├── benefits.j2
│       ├── economics.j2
│       ├── competition.j2
│       ├── market.j2
│       ├── roadmap.j2
│       ├── government.j2
│       ├── team.j2
│       ├── cta.j2
│       ├── quote.j2
│       ├── timeline.j2
│       ├── stats.j2
│       ├── faq.j2
│       └── contact.j2
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI
├── output/                  # Сгенерированные файлы
└── assets/
    └── fonts/               # Шрифты Inter и Oswald
```

## Дизайн-система

Основана на референсе polyscop.shtab-ai.ru:
- Фон: #040A14
- Акцент: #00E5FF
- Текст: #E6F1FF
- Формат: 16:9 (256mm × 144mm)
- Шрифты: Inter (заголовки, текст), Oswald (заголовки разделов)

## Типы слайдов

Поддерживается 18 типов: hero, problem, solution, how, benefits, economics, competition, market, roadmap, government, team, cta, quote, timeline, stats, faq, contact, section.

Каждый тип — отдельный шаблон в `templates/slides/<type>.j2`. Чтобы добавить новый тип:

1. Создайте `templates/slides/mytype.j2` с разметкой слайда
2. Добавьте слайд в JSON: `{"type": "mytype", ...}`
3. Шаблон автоматически подключится через `{% include 'slides/' ~ slide.type ~ '.j2' %}`

## Тестирование

```bash
pytest -q
```

## Автор

Сова (owl) — LabDoctorM, 2026-06-24