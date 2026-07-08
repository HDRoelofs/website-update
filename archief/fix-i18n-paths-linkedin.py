from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANGS = {"en", "de", "es"}
LINKEDIN = "https://www.linkedin.com/in/henk-roelofs/?locale=nl"


def is_language_subpage(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return len(rel.parts) >= 3 and rel.parts[0] in LANGS and path.name == "index.html"


def fix_language_asset_paths(text: str) -> str:
    replacements = {
        'href="../assets': 'href="../../assets',
        'src="../assets': 'src="../../assets',
        'content="../assets': 'content="../../assets',
        'data-src="../assets': 'data-src="../../assets',
        'srcset="../assets': 'srcset="../../assets',
        'url("../assets': 'url("../../assets',
        "url('../assets": "url('../../assets",
        "url(../assets": "url(../../assets",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


changed = []

for path in ROOT.rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    new = text

    while LINKEDIN + "?locale=nl" in new:
        new = new.replace(LINKEDIN + "?locale=nl", LINKEDIN)
    new = new.replace("https://www.linkedin.com/henkroelofs?_l=en_US", LINKEDIN)
    new = new.replace("https://www.linkedin.com/henkroelofs", LINKEDIN)

    if is_language_subpage(path):
        new = fix_language_asset_paths(new)

    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

print(f"Changed {len(changed)} files")
for item in changed:
    print(item)
