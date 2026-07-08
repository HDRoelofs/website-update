from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EXTS = {".html", ".css", ".js", ".txt", ".md", ".py"}

REPLACEMENTS = {
    "emoji-loader.min.js": "emoji-loader.min.js",
    "emoji-release.min.js": "emoji-release.min.js",
    "Lokale fotoverzameling van LE-Network. De foto's staan direct in deze statische site en blijven daardoor zichtbaar op GitHub Pages.": "Lokale fotoverzameling van LE-Network. De foto's staan direct in deze statische site en blijven daardoor zichtbaar op GitHub Pages.",
    "Lokale fotoverzameling van LE-Network. De foto's staan direct in deze statische site en blijven daardoor zichtbaar op GitHub Pages.": "Lokale fotoverzameling van LE-Network. De foto's staan direct in deze statische site en blijven daardoor zichtbaar op GitHub Pages.",
    "Local LE-Network photo collection. The photos are stored directly in this static site so they remain visible on GitHub Pages.": "Local LE-Network photo collection. The photos are stored directly in this static site so they remain visible on GitHub Pages.",
    "Lokale Fotosammlung von LE-Network. Die Fotos sind direkt Teil dieser statischen Website und bleiben dadurch auf GitHub Pages sichtbar.": "Lokale Fotosammlung von LE-Network. Die Fotos sind direkt Teil dieser statischen Website und bleiben dadurch auf GitHub Pages sichtbar.",
    "Colección local de fotos de LE-Network. Las fotos forman parte directa de este sitio estático para que sigan visibles en GitHub Pages.": "Colección local de fotos de LE-Network. Las fotos forman parte directa de este sitio estático para que sigan visibles en GitHub Pages.",
}


def clean(text: str) -> str:
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(r"/\*![\s\S]*?This theme, like het oude systeem,[\s\S]*?\*/", "", text, flags=re.I)
    text = text.replace("het oude systeem", "het oude systeem")
    text = text.replace("oude-systeem", "oude-systeem")
    text = text.replace("oude fotoalbums", "oude fotoalbums")
    text = text.replace("fotoarchief", "fotoarchief")
    return text


changed = []
for path in ROOT.rglob("*"):
    if ".git" in path.parts or not path.is_file() or path.suffix.lower() not in EXTS:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    new = clean(text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

print(f"changed {len(changed)} files")
for item in changed:
    print(item)
