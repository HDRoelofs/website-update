from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    "nl": "Fotoarchief",
    "en": "Photo archive",
    "de": "Fotoarchiv",
    "es": "Archivo de fotos",
}
ROUTES = {
    "nl": "foto-gallerijen",
    "en": "photo-galleries",
    "de": "fotogalerien",
    "es": "galerias-de-fotos",
}


def lang_for(path: Path) -> str:
    parts = path.relative_to(ROOT).parts
    return parts[0] if parts and parts[0] in ("en", "de", "es") else "nl"


changed = []
for path in ROOT.rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    lang = lang_for(path)
    route = ROUTES[lang]
    label = LABELS[lang]
    pattern = re.compile(rf'(<a href="[^"]*{re.escape(route)}/">)fotoarchief(</a>)')
    new = pattern.sub(rf"\1{label}\2", text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

print(f"renamed {len(changed)} picasa link labels")
for item in changed:
    print(item)
