#!/usr/bin/env -S python3
"""Render a Markdown file to a polished PDF via pandoc + xelatex.

Usage:
    python3 scripts/render_pdf.py --input reports/briefing.md --output reports/briefing.pdf [--language zh]
"""

import argparse
import os
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("render_pdf")

UTILS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")
TEMPLATE = os.path.join(UTILS_DIR, "briefing_template.tex")


def render(md_path: str, pdf_path: str, language: str = "zh"):
    """Render Markdown to PDF via pandoc + xelatex."""

    # Check pandoc
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.error("pandoc not found. Install: brew install pandoc")
        sys.exit(1)

    # Check xelatex
    try:
        subprocess.run(["xelatex", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.error("xelatex not found. Install: brew install --cask mactex")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(pdf_path)), exist_ok=True)

    cmd = [
        "pandoc", md_path,
        "-o", pdf_path,
        "--pdf-engine=xelatex",
        "-V", "fontsize=11pt",
        "-V", "linestretch=1.5",
        "--highlight-style=tango",
    ]

    # Use custom template if available
    if os.path.exists(TEMPLATE):
        cmd.extend(["--template", TEMPLATE])
    else:
        # Fallback: basic pandoc with CJK font
        logger.warning(f"Template not found: {TEMPLATE}, using basic pandoc")
        cmd.extend([
            "-V", "CJKmainfont=PingFang SC",
            "-V", "mainfont=PingFang SC",
            "-V", "monofont=Menlo",
            "-V", "geometry:margin=2.5cm",
            "-V", "colorlinks=true",
            "-V", "urlcolor=NavyBlue",
        ])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Filter out non-critical warnings
        errors = [l for l in result.stderr.splitlines()
                  if not l.startswith("[WARNING]")]
        if errors:
            logger.error("pandoc failed:\n" + "\n".join(errors))
            sys.exit(1)

    logger.info(f"PDF rendered: {pdf_path}")


def main():
    parser = argparse.ArgumentParser(description="Render Markdown to PDF")
    parser.add_argument("--input", "-i", required=True, help="Input Markdown file")
    parser.add_argument("--output", "-o", required=True, help="Output PDF file")
    parser.add_argument("--language", "-l", default="zh", help="Language (zh/en)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    render(args.input, args.output, args.language)


if __name__ == "__main__":
    main()
