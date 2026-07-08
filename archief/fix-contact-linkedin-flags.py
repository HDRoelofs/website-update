from pathlib import Path
root = Path('.')
correct_link = 'https://www.linkedin.com/in/henk-roelofs/?locale=nl'
old_links = [
    'https://www.linkedin.com/henkroelofs?_l=en_US',
    'https://www.linkedin.com/henkroelofs',
    'https://www.linkedin.com/in/henk-roelofs/',
]
changed = []
for path in root.rglob('*.html'):
    if '.git' in path.parts:
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    new = text
    for old in old_links:
        new = new.replace(old, correct_link)
    for code in ('nl','en','de','es'):
        new = new.replace(f'flags{code}.png', f'flags/{code}.png')
    # Keep contact icon and text together on one line and avoid awkward wrapping.
    new = new.replace('.item--button .fa{margin-right:.45em}', '.item--button .fa{margin-right:.45em;flex:0 0 auto}.item--button.is-icon-before{display:inline-flex!important;align-items:center!important;gap:.45em!important;white-space:nowrap!important}.item--button.is-icon-before .fa{margin-right:0!important}')
    # If generated pages do not have the stronger rule yet, append it inside social fallback style.
    if 'static-social-icons-style' in new and 'white-space:nowrap!important' not in new:
        new = new.replace('</style></head>', '.item--button .fa{margin-right:.45em;flex:0 0 auto}.item--button.is-icon-before{display:inline-flex!important;align-items:center!important;gap:.45em!important;white-space:nowrap!important}.item--button.is-icon-before .fa{margin-right:0!important}</style></head>', 1)
    if new != text:
        path.write_text(new, encoding='utf-8', newline='')
        changed.append(str(path))
for p in changed:
    print('fixed', p)
print('changed', len(changed))
