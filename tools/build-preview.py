"""Make the shareable Claude preview page from index.html.

The preview host wraps the page in its own <html>/<head>/<body>, so this strips those
tags and shortens the tab title. CSS, JS and assets are published alongside it unchanged.
Usage: python3 tools/build-preview.py <out.html>
"""
import re
import sys
from pathlib import Path

src = Path(__file__).resolve().parent.parent / "index.html"
html = src.read_text()
html = re.sub(r"<!doctype html>\s*", "", html, flags=re.I)
html = re.sub(r"</?html[^>]*>\s*|</?head>\s*|</?body>\s*", "", html)
html = re.sub(r"<title>.*?</title>", "<title>Shashwat Nritya Kala Kendra</title>", html, count=1, flags=re.S)
Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
Path(sys.argv[1]).write_text(html)
print(f"wrote {sys.argv[1]} ({len(html) // 1024} KB)")
