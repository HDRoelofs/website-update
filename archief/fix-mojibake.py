from pathlib import Path
root = Path('.')
repls = {
    'â€œ': '“', 'â€\x9d': '”', 'â€\x9c': '“', 'â€': '”',
    'â€™': '’', 'â€˜': '‘', 'â€“': '–', 'â€”': '—', 'â€¦': '…',
    'â‚¬': '€', 'Â£': '£', 'Â©': '©', 'Â®': '®', 'Â°': '°',
    'Â\xa0': '&nbsp;', 'Â ': ' ', 'Â': '',
    'Ã«': 'ë', 'Ã©': 'é', 'Ã¨': 'è', 'Ã¯': 'ï', 'Ã¶': 'ö', 'Ã¼': 'ü',
    'Ã¡': 'á', 'Ã³': 'ó', 'Ãº': 'ú', 'Ã±': 'ñ', 'Ã§': 'ç',
    'Ã‰': 'É', 'Ã‹': 'Ë', 'Ãœ': 'Ü', 'Ã–': 'Ö',
}
patterns = ('â', 'Ã', 'Â')
changed = []
for path in root.rglob('*'):
    if path.is_dir() or '.git' in path.parts:
        continue
    if path.suffix.lower() not in {'.html', '.json', '.txt', '.xml'}:
        continue
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    if not any(p in text for p in patterns):
        continue
    new = text
    for bad, good in repls.items():
        new = new.replace(bad, good)
    if new != text:
        path.write_text(new, encoding='utf-8', newline='')
        changed.append(str(path))
for p in changed:
    print('fixed', p)
print('changed', len(changed))
