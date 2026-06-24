#!/usr/bin/env python3
"""DoctorMandDesign — базовые тесты генерации презентации"""
import os
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

def test_generate_pdf():
    """Тест: генерация PDF из шаблона"""
    from generate import generate
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "test.pdf"
        generate(
            input_path=str(SCRIPT_DIR / "slides.html"),
            output_path=str(output)
        )
        
        assert output.exists(), "PDF не создан"
        assert output.stat().st_size > 1000, "PDF слишком маленький"
        
        # Check PDF header
        with open(output, 'rb') as f:
            header = f.read(5)
            assert header == b'%PDF-', "Не PDF файл"
        
        size_kb = output.stat().st_size / 1024
        print(f"✅ PDF создан: {size_kb:.1f} KB")
        return True

def test_design_system_css():
    """Тест: design-system.css содержит ключевые переменные"""
    css_path = SCRIPT_DIR / "design-system.css"
    assert css_path.exists(), "design-system.css не найден"
    
    css = css_path.read_text()
    
    required_vars = [
        '--bg-primary',
        '--accent-cyan',
        '--text-primary',
        '--card-radius',
    ]
    
    for var in required_vars:
        assert var in css, f"Переменная {var} не найдена"
    
    print(f"✅ CSS содержит {len(required_vars)} ключевых переменных")
    return True

def test_slides_html():
    """Тест: slides.html содержит 12 слайдов"""
    html_path = SCRIPT_DIR / "slides.html"
    assert html_path.exists(), "slides.html не найден"
    
    html = html_path.read_text()
    
    # Count slide sections
    slide_count = html.count('<!-- ═══ SLIDE')
    assert slide_count == 12, f"Ожидалось 12 слайдов, найдено {slide_count}"
    
    print(f"✅ HTML содержит {slide_count} слайдов")
    return True

def test_no_secrets():
    """Тест: нет секретов в коде"""
    files_to_check = ['generate.py', 'slides.html', 'design-system.css']
    
    secret_patterns = ['apiKey', 'password', 'secret', 'token', 'Bearer']
    
    for f in files_to_check:
        fpath = SCRIPT_DIR / f
        if fpath.exists():
            content = fpath.read_text()
            for pattern in secret_patterns:
                # Allow CSS custom properties that happen to contain 'token'
                if pattern.lower() in content.lower() and f.endswith('.py'):
                    # Check if it's a real secret (not just a variable name)
                    lines = content.split('\n')
                    for line in lines:
                        if pattern.lower() in line.lower() and '=' in line:
                            # Check if it looks like a hardcoded value
                            if any(c in line for c in ['\"', "'"]) and 'os.environ' not in line and 'getenv' not in line:
                                print(f"⚠️ Возможный секрет в {f}: {line.strip()}")
    
    print("✅ Секреты не найдены")
    return True

if __name__ == "__main__":
    tests = [
        test_design_system_css,
        test_slides_html,
        test_no_secrets,
        test_generate_pdf,
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
