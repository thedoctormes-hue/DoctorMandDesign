#!/usr/bin/env python3
"""DoctorMandDesign — Presentation Generator (Jinja2 + WeasyPrint)

Usage:
    python3 generate.py --data example-data.json --output output/slides.pdf
    python3 generate.py --input old-template.html --output output/legacy.pdf
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader, select_autoescape

SCRIPT_DIR = Path(__file__).parent
DEFAULT_OUTPUT = SCRIPT_DIR / "output" / "slides.pdf"

def generate(data_path: str = None, input_path: str = None, output_path: str = None):
    output = Path(output_path) if output_path else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)

    # ── Mode 1: JSON → Jinja2 ──
    if data_path:
        data_f = Path(data_path)
        if not data_f.exists():
            print(f"ERROR: Data file not found: {data_f}")
            sys.exit(1)
        with open(data_f, "r", encoding="utf-8") as f:
            payload = json.load(f)

        env = Environment(
            loader=FileSystemLoader(searchpath=[str(SCRIPT_DIR), str(SCRIPT_DIR / "templates"), str(SCRIPT_DIR / "templates" / "slides")]),
            autoescape=select_autoescape(["html", "xml"]),
        )
        tmpl = env.get_template("template.j2")
        rendered_html = tmpl.render(**payload)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", encoding="utf-8", delete=False, dir=str(SCRIPT_DIR)
        ) as tmp_f:
            tmp_f.write(rendered_html)
            tmp_path = tmp_f.name

        print(f"Data     : {data_f}")
        print(f"Output   : {output}")

        HTML(filename=tmp_path).write_pdf(target=str(output))

        try:
            Path(tmp_path).unlink()
        except OSError:
            pass

    # ── Mode 2: Legacy HTML direct ──
    elif input_path:
        template = Path(input_path)
        if not template.exists():
            print(f"ERROR: Template not found: {template}")
            sys.exit(1)

        print(f"Template : {template}")
        print(f"Output   : {output}")

        HTML(filename=str(template)).write_pdf(target=str(output))

    else:
        print("ERROR: Provide either --data (JSON) or --input (HTML)")
        sys.exit(1)

    size_kb = output.stat().st_size / 1024
    print(f"Done! {size_kb:.1f} KB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate presentation PDF")
    parser.add_argument("--data", "-d", help="Path to JSON data file (uses Jinja2→template.j2)")
    parser.add_argument("--input", "-i", help="Raw HTML template (legacy mode)")
    parser.add_argument("--output", "-o", help="PDF output path")
    args = parser.parse_args()
    generate(data_path=args.data, input_path=args.input, output_path=args.output)
