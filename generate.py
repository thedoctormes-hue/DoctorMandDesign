#!/usr/bin/env python3
"""DoctorMandDesign — Presentation Generator
Usage: python3 generate.py [--input data.html] [--output output/slides.pdf]
"""
import argparse
import os
import sys
from pathlib import Path
from weasyprint import HTML

SCRIPT_DIR = Path(__file__).parent
DEFAULT_TEMPLATE = SCRIPT_DIR / "slides.html"
DEFAULT_OUTPUT = SCRIPT_DIR / "output" / "slides.pdf"

def generate(input_path: str = None, output_path: str = None):
    template = Path(input_path) if input_path else DEFAULT_TEMPLATE
    output = Path(output_path) if output_path else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)

    if not template.exists():
        print(f"ERROR: Template not found: {template}")
        sys.exit(1)

    print(f"Template : {template}")
    print(f"Output   : {output}")

    HTML(filename=str(template)).write_pdf(target=str(output))

    size_kb = output.stat().st_size / 1024
    print(f"Done! {size_kb:.1f} KB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate presentation PDF")
    parser.add_argument("--input", "-i", help="HTML template path")
    parser.add_argument("--output", "-o", help="PDF output path")
    args = parser.parse_args()
    generate(args.input, args.output)
