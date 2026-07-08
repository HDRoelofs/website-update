from pathlib import Path
from html import escape
import re


ROOT = Path(__file__).resolve().parents[1]
UPLOADS = ROOT / "assets" / "uploads"

LANG_PAGES = {
    "nl": {
        "route": "foto-gallerijen",
        "title": "Foto galerijen",
        "intro": "Lokale fotoverzameling van LE-Network. De foto's staan direct in deze statische site en blijven daardoor zichtbaar op GitHub Pages.",
        "back": "Terug naar home",
    },
    "en": {
        "route": "photo-galleries",
        "title": "Photo galleries",
        "intro": "Local LE-Network photo collection. The photos are stored directly in this static site so they remain visible on GitHub Pages.",
        "back": "Back to home",
    },
    "de": {
        "route": "fotogalerien",
        "title": "Fotogalerien",
        "intro": "Lokale Fotosammlung von LE-Network. Die Fotos sind direkt Teil dieser statischen Website und bleiben dadurch auf GitHub Pages sichtbar.",
        "back": "Zurück zur Startseite",
    },
    "es": {
        "route": "galerias-de-fotos",
        "title": "Galerías de fotos",
        "intro": "Colección local de fotos de LE-Network. Las fotos forman parte directa de este sitio estático para que sigan visibles en GitHub Pages.",
        "back": "Volver al inicio",
    },
}

IMAGE_RE = re.compile(r"\.(jpe?g|png|gif|webp)$", re.I)
SIZE_RE = re.compile(r"-(\d{2,5})x(\d{2,5})(?=\.[^.]+$)", re.I)
SKIP_RE = re.compile(
    r"(favicon|cropped-favicon|logo|banner|snn|europe|catent|stenden|nhl|entreprenasium|jbms|edubanner|learngamesbanner|lenetworkbanner)",
    re.I,
)


def media_key(path: Path) -> str:
    name = path.name
    name = SIZE_RE.sub("", name)
    name = re.sub(r"-scaled(?=\.[^.]+$)", "", name, flags=re.I)
    return str(path.parent.relative_to(UPLOADS) / name).lower()


def collect_images() -> list[Path]:
    candidates = []
    for path in UPLOADS.rglob("*"):
        if not path.is_file() or not IMAGE_RE.search(path.name):
            continue
        rel = path.relative_to(UPLOADS).as_posix()
        if "leerpretpark/" in rel or SKIP_RE.search(path.name):
            continue
        if path.stat().st_size < 15_000:
            continue
        candidates.append(path)

    best = {}
    for path in candidates:
        key = media_key(path)
        current = best.get(key)
        if current is None or path.stat().st_size > current.stat().st_size:
            best[key] = path
    return sorted(best.values(), key=lambda p: p.relative_to(UPLOADS).as_posix().lower())


def caption(path: Path) -> str:
    name = SIZE_RE.sub("", path.stem)
    name = re.sub(r"-scaled.*$", "", name, flags=re.I)
    name = re.sub(r"[_-]+", " ", name).strip()
    year_month = "/".join(path.relative_to(UPLOADS).parts[:2])
    return f"{name} ({year_month})"


def rel_from_page(page_dir: Path, target: Path) -> str:
    import os
    return os.path.relpath(target, page_dir).replace("\\", "/")


def render_page(lang: str, images: list[Path]) -> str:
    info = LANG_PAGES[lang]
    route = info["route"]
    page_dir = ROOT / route if lang == "nl" else ROOT / lang / route
    home = "../" if lang == "nl" else "../../"
    cards = []
    for image in images:
        href = rel_from_page(page_dir, image)
        cards.append(
            f'<a class="gallery-card" href="{href}" target="_blank" rel="noopener">'
            f'<img src="{href}" alt="{escape(caption(image))}" loading="lazy">'
            f'<span>{escape(caption(image))}</span>'
            f'</a>'
        )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(info["title"])} - LE-Network</title>
<link rel="icon" href="{home}assets/uploads/2019/10/cropped-favicon-32x32.png" sizes="32x32">
<style>
body{{margin:0;font-family:Arial,Helvetica,sans-serif;color:#1f2d33;background:#fff}}
.site-header{{border-bottom:1px solid #d8e2e7;background:#fff}}
.inner{{max-width:1180px;margin:0 auto;padding:24px}}
.brand{{display:flex;align-items:center;gap:14px;color:#1f2d33;text-decoration:none;font-weight:700;font-size:24px}}
.brand img{{width:151px;height:auto}}
.topline{{display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap}}
.back{{color:#1e88c8;text-decoration:none;font-weight:700}}
h1{{margin:34px 0 10px;color:#1e88c8;font-weight:300;font-size:48px;line-height:1.1}}
.intro{{max-width:860px;font-size:18px;line-height:1.6;margin:0 0 28px}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:18px;padding:0 0 48px}}
.gallery-card{{display:block;min-height:260px;border:1px solid #d7e0e5;text-decoration:none;color:#1f2d33;background:#f7f9fa;overflow:hidden}}
.gallery-card img{{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#dce3e6}}
.gallery-card span{{display:block;padding:12px 14px;font-size:15px;line-height:1.35}}
@media(max-width:640px){{h1{{font-size:38px}}.inner{{padding:18px}}.brand img{{width:130px}}}}
</style>
</head>
<body>
<header class="site-header"><div class="inner topline"><a class="brand" href="{home}"><img src="{home}assets/uploads/2019/10/LEnetwork.png" alt="LE-Network"></a><a class="back" href="{home}">{escape(info["back"])}</a></div></header>
<main class="inner">
<h1>{escape(info["title"])}</h1>
<p class="intro">{escape(info["intro"])}</p>
<div class="gallery">
{''.join(cards)}
</div>
</main>
</body>
</html>
"""


def gallery_href(from_file: Path, lang: str) -> str:
    route = LANG_PAGES[lang]["route"]
    target = ROOT / route / "index.html" if lang == "nl" else ROOT / lang / route / "index.html"
    return rel_from_page(from_file.parent, target.parent) + "/"


def page_lang(path: Path) -> str:
    rel = path.relative_to(ROOT).parts
    return rel[0] if rel and rel[0] in ("en", "de", "es") else "nl"


def replace_picasa_links():
    pattern = re.compile(r'href="https://plus\.google\.com/photos/117353890407907733141/albums\?banner=pwa"')
    changed = []
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "plus.google.com/photos/117353890407907733141/albums" not in text:
            continue
        lang = page_lang(path)
        new = pattern.sub(f'href="{gallery_href(path, lang)}"', text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())
    return changed


images = collect_images()
for lang, info in LANG_PAGES.items():
    page = ROOT / info["route"] / "index.html" if lang == "nl" else ROOT / lang / info["route"] / "index.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(render_page(lang, images), encoding="utf-8")

changed = replace_picasa_links()
print(f"gallery images: {len(images)}")
print("gallery pages:")
for info in LANG_PAGES.values():
    print(info["route"])
print(f"updated picasa links in {len(changed)} files")
for item in changed:
    print(item)
