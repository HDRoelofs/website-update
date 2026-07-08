from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTS = {".html", ".css", ".js", ".txt", ".md"}
REPL = {
    "wp-emoji": "emoji",
    "_wpemojiSettings": "_emojiSettings",
    "wpEmojiSettingsSupports": "emojiSettingsSupports",
    "wpemoji": "siteemoji",
    "wpa.css": "form-check.css",
    "wpa.js": "form-check.js",
}


changed = []
for path in ROOT.rglob("*"):
    if ".git" in path.parts or "archief" in path.parts or not path.is_file() or path.suffix.lower() not in EXTS:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    new = text
    for old, repl in REPL.items():
        new = new.replace(old, repl)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

print(f"changed {len(changed)} files")
for item in changed:
    print(item)
