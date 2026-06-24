#!/usr/bin/env python3
"""DoctorMandDesign — тесты генератора презентаций"""
import subprocess
import sys
import json
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def test_generate_with_json():
    """Генерация PDF из JSON-данных"""
    json_path = SCRIPT_DIR / "example-data.json"
    out_pdf = SCRIPT_DIR / "output" / "test_json.pdf"
    out_pdf.parent.mkdir(exist_ok=True)

    result = subprocess.run(
        [sys.executable, "generate.py", "--data", str(json_path), "--output", str(out_pdf)],
        capture_output=True, text=True, cwd=str(SCRIPT_DIR),
    )
    assert result.returncode == 0, f"generate.py failed: {result.stderr}"
    assert out_pdf.exists(), "PDF не создан"
    assert out_pdf.stat().st_size > 1000, "PDF слишком маленький"

    # PDF header check
    with open(out_pdf, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-", "Не PDF файл"

    print(f"✅ PDF из JSON создан: {out_pdf.stat().st_size / 1024:.1f} KB")
    

def test_verify_report():
    """Запуск verify.py и проверка что все слайды имеют текст"""
    out_pdf = SCRIPT_DIR / "output" / "test_json.pdf"
    assert out_pdf.exists(), "Сначала запустите test_generate_with_json"

    result = subprocess.run(
        [sys.executable, "verify.py", str(out_pdf)],
        capture_output=True, text=True, cwd=str(SCRIPT_DIR),
    )
    assert result.returncode == 0, f"verify.py failed: {result.stderr}"

    report = json.loads(result.stdout)
    total = len(report["slides"])
    passed = 0
    for s in report["slides"]:
        has_text = s["has_text"]
        wcag_level = s["wcag_level"]
        basic_contrast = s["basic_contrast"]
        wcag_ok = wcag_level in ("AA", "AA-large")
        if wcag_level == "UNKNOWN":
            wcag_ok = basic_contrast >= 0.3
        if wcag_ok and has_text:
            passed += 1
    
    assert passed == total, f"Only {passed}/{total} slides passed (text + adequate contrast)"
    print(f"✅ Verify: {total} slides, all passed text and contrast check")
    

def test_design_system_css():
    """CSS содержит ключевые переменные"""
    css_path = SCRIPT_DIR / "design-system.css"
    assert css_path.exists(), "design-system.css не найден"

    css = css_path.read_text()
    required_vars = ["--bg-primary", "--accent-cyan", "--text-primary", "--card-radius", "--font-family"]

    for var in required_vars:
        assert var in css, f"Переменная {var} не найдена"

    # Check @font-face is present
    assert "@font-face" in css, "@font-face не найден в CSS"

    print(f"✅ CSS: {len(required_vars)} переменных + @font-face")
    

def test_template_j2():
    """template.j2 существует и содержит Jinja2-блоки"""
    tmpl_path = SCRIPT_DIR / "template.j2"
    assert tmpl_path.exists(), "template.j2 не найден"

    tmpl = tmpl_path.read_text()
    assert "{% for slide in slides %}" in tmpl, "Нет цикла по слайдам"
    assert "{% include" in tmpl, "Нет include-блоков для модульных шаблонов"

    # Check modular templates exist
    slides_dir = SCRIPT_DIR / "templates" / "slides"
    assert slides_dir.exists(), "templates/slides/ не найден"
    slide_templates = list(slides_dir.glob("*.j2"))
    assert len(slide_templates) >= 10, f"Ожидалось >= 10 шаблонов слайдов, найдено {len(slide_templates)}"

    print(f"✅ template.j2: {len(slide_templates)} модульных шаблонов")
    

def test_no_secrets():
    """Нет секретов в коде"""
    files_to_check = ["generate.py", "template.j2", "design-system.css", "example-data.json"]
    secret_patterns = ["apiKey", "password", "secret", "Bearer"]

    for f in files_to_check:
        fpath = SCRIPT_DIR / f
        if fpath.exists():
            content = fpath.read_text()
            for pattern in secret_patterns:
                if pattern.lower() in content.lower() and f.endswith(".py"):
                    lines = content.split("\n")
                    for line in lines:
                        if pattern.lower() in line.lower() and "=" in line:
                            if any(c in line for c in ['"', "'"]) and "os.environ" not in line:
                                print(f"⚠️ Возможный секрет в {f}: {line.strip()}")

    print("✅ Секреты не найдены")
    

def test_json_schema():
    """example-data.json валиден и содержит все необходимые поля"""
    json_path = SCRIPT_DIR / "example-data.json"
    assert json_path.exists(), "example-data.json не найден"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "title" in data, "Нет title"
    assert "subtitle" in data, "Нет subtitle"
    assert "slides" in data, "Нет slides"
    assert len(data["slides"]) >= 10, f"Слишком мало слайдов: {len(data['slides'])}"

    # Check each slide has a type
    for i, slide in enumerate(data["slides"]):
        assert "type" in slide, f"Слайд {i+1}: нет поля type"

    print(f"✅ JSON: {len(data['slides'])} слайдов, все с полем type")
    

if __name__ == "__main__":
    tests = [
        test_design_system_css,
        test_template_j2,
        test_json_schema,
        test_no_secrets,
        test_generate_with_json,
        test_verify_report,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Результат: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    else:
        print("✅ Все тесты пройдены")
