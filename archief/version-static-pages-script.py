from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
VERSION = "20260708-mobile-menu-2"


changed = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts or "archief" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    new = re.sub(r'(src="[^"]*assets/static-pages\.js)(?:\?v=[^"]*)?(")', rf"\1?v={VERSION}\2", text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

print(f"versioned static-pages.js in {len(changed)} files")
for item in changed:
    print(item)
