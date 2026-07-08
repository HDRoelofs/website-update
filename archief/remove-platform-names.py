from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTS = {".html", ".css", ".js", ".xml", ".txt", ".json", ".php", ".py", ".md"}
PUBLIC_SKIP_DIRS = {".git"}


def should_process(path: Path) -> bool:
    if any(part in PUBLIC_SKIP_DIRS for part in path.parts):
        return False
    return path.is_file() and path.suffix.lower() in TEXT_EXTS


def clean_html(text: str) -> str:
    # Remove CMS discovery/meta noise from the generated static pages.
    text = re.sub(r'<meta\s+content="het oude systeem[^"]*"\s+name="generator"\s*/?>', "", text, flags=re.I)
    text = re.sub(r'<generator>https://oude-systeem\.org/\?v=[^<]+</generator>\s*', "", text, flags=re.I)
    text = re.sub(r'<link[^>]+rel="https://api\.w\.org/"[^>]*>', "", text, flags=re.I)
    text = re.sub(r'<link[^>]+site-data[^>]+>', "", text, flags=re.I)
    text = re.sub(r'<link[^>]+xmlrpc\.php\?rsd[^>]+>', "", text, flags=re.I)
    text = re.sub(r'/\*# sourceURL=[^*]*(?:site-includes|assets)[^*]*\*/', "", text, flags=re.I)

    # Static asset paths should not expose het oude systeem folder names.
    text = text.replace("assets", "assets")
    text = text.replace("site-includes", "site-includes")
    text = text.replace("site-data", "site-data")

    # Remove public copy that described the archive as coming from het oude systeem.
    replacements = {
        "Lokale fotoverzameling van LE-Network. De foto's staan direct in deze statische site en blijven daardoor zichtbaar op GitHub Pages.": "Lokale fotoverzameling van LE-Network. De foto's staan direct in deze statische site en blijven daardoor zichtbaar op GitHub Pages.",
        "Local LE-Network photo collection. The photos are stored directly in this static site so they remain visible on GitHub Pages.": "Local LE-Network photo collection. The photos are stored directly in this static site so they remain visible on GitHub Pages.",
        "Lokale Fotosammlung von LE-Network. Die Fotos sind direkt Teil dieser statischen Website und bleiben dadurch auf GitHub Pages sichtbar.": "Lokale Fotosammlung von LE-Network. Die Fotos sind direkt Teil dieser statischen Website und bleiben dadurch auf GitHub Pages sichtbar.",
        "Colección local de fotos de LE-Network. Las fotos forman parte directa de este sitio estático para que sigan visibles en GitHub Pages.": "Colección local de fotos de LE-Network. Las fotos forman parte directa de este sitio estático para que sigan visibles en GitHub Pages.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


changed = []
for path in ROOT.rglob("*"):
    if not should_process(path):
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    new = clean_html(text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

print(f"cleaned {len(changed)} files")
for item in changed:
    print(item)
