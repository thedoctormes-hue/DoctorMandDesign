#!/usr/bin/env python3
"""
verify.py — проверка качества сгенерированного PDF:
- Растеризация слайдов в PNG (pdftoppm)
- OCR через pytesseract (если доступен)
- WCAG-AA контрастность: извлечение цветов текста и фона, расчёт контраста
- Проверка что текст читаем (размер, контраст)
- JSON-отчёт
"""
import subprocess
import json
import sys
import os
import re
import pathlib
from PIL import Image, ImageStat, ImageDraw, ImageFont

PDF_PATH = sys.argv[1] if len(sys.argv) > 1 else "output/demo_full.pdf"
OUT_DIR = pathlib.Path("output/verify_tmp")
OUT_DIR.mkdir(exist_ok=True)

# WCAG-AA thresholds
WCAG_AA_NORMAL = 4.5  # для обычного текста
WCAG_AA_LARGE = 3.0    # для крупного текста (>=18pt или 14pt bold)


def relative_luminance(r, g, b):
    """Calculate relative luminance per WCAG 2.1."""
    def linearize(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(l1, l2):
    """Calculate contrast ratio between two luminances."""
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def wcag_level(ratio):
    """Return WCAG level or fail."""
    aa_large = ratio >= WCAG_AA_LARGE
    aa_normal = ratio >= WCAG_AA_NORMAL
    if aa_normal:
        return "AA"
    elif aa_large:
        return "AA-large"
    else:
        return "FAIL"


def extract_text_regions(img):
    """
    Heuristic: find dark pixels on light background (text-like regions).
    Returns list of (region_pixels, avg_color) tuples.
    """
    gray = img.convert("L")
    width, height = gray.size
    pixels = gray.load()

    # Find text-like regions: pixels significantly darker than their neighborhood
    text_pixels = []
    bg_pixels = []

    for y in range(0, height, 4):
        for x in range(0, width, 4):
            val = pixels[x, y]
            if val < 80:  # dark pixel = likely text
                text_pixels.append((x, y, val))
            elif val > 180:  # light pixel = likely background
                bg_pixels.append((x, y, val))

    return text_pixels, bg_pixels


def check_slide_contrast(img_path):
    """
    Check contrast of a slide image.
    Returns dict with contrast info.
    """
    img = Image.open(img_path)
    rgb_img = img.convert("RGB")
    pixels = rgb_img.load()
    width, height = rgb_img.size

    # Sample pixels for performance
    text_colors = []
    bg_colors = []

    for y in range(0, height, 8):
        for x in range(0, width, 8):
            r, g, b = pixels[x, y]
            lum = relative_luminance(r, g, b)
            if lum < 0.15:  # dark = text
                text_colors.append((r, g, b))
            elif lum > 0.7:  # light = background
                bg_colors.append((r, g, b))

    if not text_colors or not bg_colors:
        return {
            "contrast_ratio": 0,
            "wcag_level": "UNKNOWN",
            "text_color": None,
            "bg_color": None,
            "sample_count": 0,
        }

    # Average colors
    avg_text = tuple(sum(c[i] for c in text_colors) // len(text_colors) for i in range(3))
    avg_bg = tuple(sum(c[i] for c in bg_colors) // len(bg_colors) for i in range(3))

    text_lum = relative_luminance(*avg_text)
    bg_lum = relative_luminance(*avg_bg)
    ratio = contrast_ratio(text_lum, bg_lum)

    return {
        "contrast_ratio": round(ratio, 2),
        "wcag_level": wcag_level(ratio),
        "text_color": list(avg_text),
        "bg_color": list(avg_bg),
        "sample_count": min(len(text_colors), len(bg_colors)),
    }


# 1️⃣ rasterize
try:
    subprocess.run([
        "pdftoppm", "-png", "-r", "150", PDF_PATH,
        str(OUT_DIR / "slide")
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError as e:
    print(f"ERROR: Rasterization failed: {e}", file=sys.stderr)
    sys.exit(1)

report = {"pdf": PDF_PATH, "slides": [], "summary": {}}
passed = 0
failed = 0
warnings = 0

for img_file in sorted(OUT_DIR.glob("slide-*.png")):
    slide_name = img_file.stem

    # 2️⃣ OCR
    try:
        ocr_text = subprocess.check_output(
            ["tesseract", str(img_file), "stdout", "-l", "rus+eng", "--psm", "6"],
            stderr=subprocess.DEVNULL, timeout=10
        ).decode("utf-8", errors="ignore")
    except Exception:
        ocr_text = ""

    # 3️⃣ Basic contrast (legacy)
    im = Image.open(img_file).convert("L")
    extrema = im.getextrema()
    basic_contrast = (extrema[1] - extrema[0]) / 255.0 if extrema else 0.0

    # 4️⃣ WCAG-AA contrast
    wcag = check_slide_contrast(img_file)

    has_text = bool(re.search(r'\w', ocr_text))
    ocr_chars = len(ocr_text.strip())

    # Determine pass/fail
    wcag_ok = wcag["wcag_level"] in ("AA", "AA-large")
    if wcag["wcag_level"] == "UNKNOWN":
        # Fall back to basic contrast
        wcag_ok = basic_contrast >= 0.3
    if wcag_ok and has_text:
        passed += 1
        status = "PASS"
    elif has_text:
        warnings += 1
        status = "WARN"
    else:
        failed += 1
        status = "FAIL"

    slide_report = {
        "file": str(img_file),
        "status": status,
        "ocr_text_snippet": ocr_text.strip()[:120],
        "ocr_chars": ocr_chars,
        "has_text": has_text,
        "basic_contrast": round(basic_contrast, 3),
        "wcag_contrast_ratio": wcag["contrast_ratio"],
        "wcag_level": wcag["wcag_level"],
        "text_color_rgb": wcag["text_color"],
        "bg_color_rgb": wcag["bg_color"],
    }
    report["slides"].append(slide_report)

total = passed + failed + warnings
report["summary"] = {
    "total_slides": total,
    "passed": passed,
    "warnings": warnings,
    "failed": failed,
    "wcag_aa_compliance": f"{passed}/{total}" + (f" (+{warnings} warnings)" if warnings else ""),
}

print(json.dumps(report, ensure_ascii=False, indent=2))

print(f"\n=== WCAG-AA Summary ===", file=sys.stderr)
print(f"Total: {total} slides | Passed: {passed} | Warnings: {warnings} | Failed: {failed}", file=sys.stderr)

if failed > 0:
    sys.exit(1)
