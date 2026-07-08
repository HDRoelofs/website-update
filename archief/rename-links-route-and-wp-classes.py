from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTS = {".html", ".css", ".js", ".txt", ".md", ".py"}

REPLACEMENTS = {
    "elementor-10378": "links",
    "plugins/elementor": "lib/page-builder",
    "uploads/elementor": "uploads/page-builder",
    "--wp--": "--site--",
    "wp-block": "site-block",
    "wp-image": "site-image",
    "wp-post-image": "site-post-image",
    "wp-element": "site-element",
    "wp-container": "site-container",
    "wp-site-blocks": "site-blocks",
}


changed = []
for path in ROOT.rglob("*"):
    if ".git" in path.parts or "archief" in path.parts or not path.is_file() or path.suffix.lower() not in EXTS:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    new = text
    for old, repl in REPLACEMENTS.items():
        new = new.replace(old, repl)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

print(f"changed {len(changed)} files")
for item in changed:
    print(item)
