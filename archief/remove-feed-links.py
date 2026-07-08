from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r'<link[^>]+comments/feed[^>]*>\s*', re.I)

changed = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts or "archief" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    new = PATTERN.sub("", text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

print(f"removed feed links from {len(changed)} files")
for item in changed:
    print(item)
