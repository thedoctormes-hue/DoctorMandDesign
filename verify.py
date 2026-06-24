#!/usr/bin/env python3
"""
verify.py — lightweight verification of generated PDF:
- Rasterizes each slide to PNG (pdftoppm)
- Runs OCR via pytesseract (if available) to ensure text is present
- Checks approximate contrast via luminance difference (WCAG-inspired)
- Outputs JSON report
"""
import subprocess, json, sys, os, pathlib, re
from PIL import Image, ImageStat

PDF_PATH = sys.argv[1] if len(sys.argv) > 1 else "output/demo_full.pdf"
OUT_DIR = pathlib.Path("output/verify_tmp")
OUT_DIR.mkdir(exist_ok=True)

# 1️⃣ rasterize
subprocess.run([
    "pdftoppm", "-png", "-r", "150", PDF_PATH,
    str(OUT_DIR / "slide")
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

report = {"pdf": PDF_PATH, "slides": []}
for img_file in sorted(OUT_DIR.glob("slide-*.png")):
    # OCR (if tesseract installed)
    try:
        ocr_text = subprocess.check_output(
            ["tesseract", str(img_file), "stdout", "-l", "rus+eng", "--psm", "6"],
            stderr=subprocess.DEVNULL, timeout=10
        ).decode("utf-8", errors="ignore")
    except Exception:
        ocr_text = ""

    # Contrast: compute luminance range
    im = Image.open(img_file).convert("L")  # grayscale
    extrema = im.getextrema()  # (min, max)
    if extrema:
        contrast = (extrema[1] - extrema[0]) / 255.0
    else:
        contrast = 0.0
    ok_contrast = contrast >= 0.3  # permissive threshold for slide backgrounds

    slide_report = {
        "file": str(img_file),
        "ocr_text_snippet": ocr_text.strip()[:120],
        "ocr_chars": len(ocr_text.strip()),
        "contrast": round(contrast, 3),
        "contrast_ok": bool(ok_contrast),
        "has_text": bool(re.search(r'\w', ocr_text))
    }
    report["slides"].append(slide_report)

print(json.dumps(report, ensure_ascii=False, indent=2))