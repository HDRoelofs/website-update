from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse, urlunparse, unquote
import json, re, time
from bs4 import BeautifulSoup, NavigableString, Comment
from deep_translator import GoogleTranslator

ROOT = Path('.').resolve()
CACHE_PATH = ROOT / 'archief' / 'translation-cache.json'
BASE_ROUTES = [
    '',
    'over-ons',
    'referenties',
    'references',
    'elementor-10378',
    'cum-laude-oksana',
    'le-network',
    'le-network-products-renamed-to-learn-games',
    'new-leadership-for-le-network',
    're-xplore-and-le-network-joining-forces',
    'relocation-of-the-le-network-office',
    'working-with-the-niet-school-initiative',
]
LANGS = {
    'nl': {'name': 'Nederlands', 'html': 'nl', 'flag': 'nl.png'},
    'en': {'name': 'English', 'html': 'en', 'flag': 'en.png'},
    'de': {'name': 'Deutsch', 'html': 'de', 'flag': 'de.png'},
    'es': {'name': 'Español', 'html': 'es', 'flag': 'es.png'},
}
SOURCE_FILES = {route: (ROOT / (route if route else '') / 'index.html') for route in BASE_ROUTES}
SOURCE_FILES[''] = ROOT / 'index.html'

cache = {}
if CACHE_PATH.exists():
    cache = json.loads(CACHE_PATH.read_text(encoding='utf-8'))
translators = {}

def route_path(lang: str, route: str) -> str:
    if lang == 'nl':
        return (route + '/' if route else './')
    return f'{lang}/{route}/' if route else f'{lang}/'

def target_file(lang: str, route: str) -> Path:
    if lang == 'nl':
        return SOURCE_FILES[route]
    return ROOT / lang / route / 'index.html' if route else ROOT / lang / 'index.html'

def rel_url(from_file: Path, lang: str, route: str, frag: str = '') -> str:
    target = target_file(lang, route)
    from_dir = from_file.parent
    rel = Path(target.parent).relative_to(ROOT).as_posix()
    # If linking to a directory index, use relative dir URL.
    href_dir = target.parent
    s = Path.cwd()
    relp = Path(Path(href_dir).resolve()).relative_to(ROOT)
    url = Path(*relp.parts).as_posix() + '/'
    if not url or url == './':
        url = './'
    # Make relative from current directory.
    current_rel = from_dir.relative_to(ROOT)
    import posixpath
    current = current_rel.as_posix()
    if current == '.':
        current = ''
    target_dir = href_dir.relative_to(ROOT).as_posix()
    if target_dir == '.': target_dir = ''
    rel_to = posixpath.relpath(target_dir or '.', current or '.')
    if rel_to == '.': rel_to = './'
    else: rel_to += '/'
    return rel_to + frag

def same_route_from_file(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == 'index.html': return ''
    if rel.endswith('/index.html'):
        parts = rel.split('/')[:-1]
        if parts and parts[0] in ('en','de','es'):
            return '/'.join(parts[1:])
        return '/'.join(parts)
    return ''

def internal_route_from_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme in ('mailto','tel','javascript') or url.startswith('#') or parsed.scheme == 'data':
        return None
    if parsed.netloc and parsed.netloc not in ('le-network.nl','www.le-network.nl'):
        return None
    path = parsed.path.strip('/')
    if path in ('', 'le-network'):
        route = '' if path == '' else 'le-network'
    else:
        if path.startswith(('en/','de/','es/')):
            path = '/'.join(path.split('/')[1:])
        route = path
    if route in BASE_ROUTES:
        return route, ('#' + parsed.fragment if parsed.fragment else '')
    return None

def translate_text(text: str, lang: str) -> str:
    if lang == 'nl': return text
    raw = text
    if not raw.strip(): return raw
    # Skip mostly symbolic/code text.
    if re.fullmatch(r'\s*[\W\d_]+\s*', raw, re.UNICODE): return raw
    key = f'{lang}\0{raw}'
    if key in cache: return cache[key]
    # Preserve whitespace around node.
    prefix = re.match(r'^\s*', raw).group(0)
    suffix = re.search(r'\s*$', raw).group(0)
    core = raw.strip()
    if not core: return raw
    # Do not translate brand/navigation atoms that should remain unchanged.
    preserve = {'LE-Network','LEARN Games','LEARNGames','LE-Game','LO-Game','LA-Game','SNN','Facebook','Flickr','fotoarchief','LinkedIn','Youtube','Instagram'}
    if core in preserve or '@' in core:
        cache[key] = raw
        return raw
    tr = translators.get(lang)
    if tr is None:
        tr = GoogleTranslator(source='auto', target=lang)
        translators[lang] = tr
    for attempt in range(3):
        try:
            translated = tr.translate(core)
            if not translated:
                translated = core
            out = prefix + translated + suffix
            cache[key] = out
            if len(cache) % 25 == 0:
                CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
            return out
        except Exception as e:
            time.sleep(1 + attempt)
    cache[key] = raw
    return raw

def translate_soup(soup: BeautifulSoup, lang: str):
    skip_parents = {'script','style','noscript','svg','code','pre'}
    for node in list(soup.find_all(string=True)):
        if isinstance(node, Comment): continue
        parent = node.parent
        if not parent or parent.name in skip_parents: continue
        if parent.get('class') and any('fa' == c or str(c).startswith('fa-') for c in parent.get('class')):
            continue
        new = translate_text(str(node), lang)
        if new != str(node):
            node.replace_with(NavigableString(new))
    # Translate selected meta/title attrs.
    for tag in soup.find_all(attrs={'content': True}):
        if tag.name == 'meta' and (tag.get('name') in ('description','twitter:title','twitter:description') or tag.get('property') in ('og:title','og:description')):
            tag['content'] = translate_text(tag.get('content',''), lang)
    if soup.html:
        soup.html['lang'] = LANGS[lang]['html']

def normalize_asset_url(url: str, source_file: Path, target: Path, lang: str) -> str:
    if not url or url.startswith(('data:', 'mailto:', 'tel:', 'javascript:')) or url.startswith('#'):
        return url
    parsed = urlparse(url)
    frag = ('#' + parsed.fragment) if parsed.fragment else ''
    query = ('?' + parsed.query) if parsed.query else ''
    internal = internal_route_from_url(url)
    if internal:
        route, f = internal
        return rel_url(target, lang, route, f)
    if parsed.scheme in ('http','https'):
        return url
    # Split relative path from query/fragment.
    path = parsed.path
    if not path:
        return url
    if path.startswith('/'):
        abs_path = ROOT / path.strip('/')
    else:
        abs_path = (source_file.parent / unquote(path)).resolve()
    try:
        rel = abs_path.relative_to(target.parent.resolve())
        new_path = rel.as_posix()
    except ValueError:
        import os
        new_path = os.path.relpath(abs_path, target.parent.resolve()).replace('\\','/')
    return new_path + query + frag

def normalize_srcset(value: str, source_file: Path, target: Path, lang: str) -> str:
    parts = []
    for item in value.split(','):
        item = item.strip()
        if not item:
            continue
        bits = item.split()
        bits[0] = normalize_asset_url(bits[0], source_file, target, lang)
        parts.append(' '.join(bits))
    return ', '.join(parts)

def normalize_inline_urls(value: str, source_file: Path, target: Path, lang: str) -> str:
    def repl(match):
        quote = match.group(1) or ''
        url = match.group(2).strip()
        return f'url({quote}{normalize_asset_url(url, source_file, target, lang)}{quote})'
    return re.sub(r'url\((["\']?)([^"\')]+)\1\)', repl, value)

def update_urls(soup: BeautifulSoup, source_file: Path, target: Path, lang: str):
    attrs = ['href','src','poster','data-src','data-lazy-src','action']
    for tag in soup.find_all(True):
        for attr in attrs:
            if tag.has_attr(attr):
                tag[attr] = normalize_asset_url(tag[attr], source_file, target, lang)
        for attr in ['srcset','data-srcset']:
            if tag.has_attr(attr):
                tag[attr] = normalize_srcset(tag[attr], source_file, target, lang)
        if tag.has_attr('style'):
            tag['style'] = normalize_inline_urls(tag['style'], source_file, target, lang)
    for style in soup.find_all('style'):
        if style.string:
            style.string.replace_with(normalize_inline_urls(str(style.string), source_file, target, lang))

def add_flag_files():
    flag_dir = ROOT / 'assets/plugins/sitepress-multilingual-cms/res/flags'
    flag_dir.mkdir(parents=True, exist_ok=True)
    # tiny inline SVG flags are enough for static switcher when WPML did not have them.
    flags = {
        'de.png': b'',
        'es.png': b'',
    }
    # Use remote lightweight flag images if local missing.
    import requests
    urls = {
        'de.png': 'https://flagcdn.com/w40/de.png',
        'es.png': 'https://flagcdn.com/w40/es.png',
    }
    for name, u in urls.items():
        p = flag_dir / name
        if not p.exists() or p.stat().st_size == 0:
            try:
                r = requests.get(u, timeout=15)
                r.raise_for_status()
                p.write_bytes(r.content)
            except Exception:
                pass

def remove_existing_switchers(soup: BeautifulSoup):
    for li in soup.select('li.menu-item-wpml-ls-static, li.wpml-ls-menu-item, li[class*="wpml-ls-item"]'):
        # Only remove menu switchers, not footer/static post translation paragraphs.
        if li.find_parent('ul', id=re.compile('menu-main')):
            li.decompose()
    for p in soup.select('p.wpml-ls-statics-post_translations'):
        p.decompose()
    for div in soup.select('div.wpml-ls-statics-footer'):
        div.decompose()

def make_lang_item(current_lang: str, route: str, file_path: Path, flag_base: str) -> str:
    current = LANGS[current_lang]
    current_href = rel_url(file_path, current_lang, route)
    lis = []
    for lang, info in LANGS.items():
        href = rel_url(file_path, lang, route)
        active = ' wpml-ls-current-language' if lang == current_lang else ''
        aria = ' aria-current="page"' if lang == current_lang else ''
        lis.append(f'<li class="menu-item wpml-ls-item wpml-ls-item-{lang}{active}"><a href="{href}" hreflang="{lang}" lang="{lang}"{aria}><span class="link-before"><img class="wpml-ls-flag" src="{flag_base}{info["flag"]}" alt="{info["name"]}">{info["name"]}</span></a></li>')
    submenu = ''.join(lis)
    return f'<li class="menu-item wpml-ls-item wpml-ls-item-{current_lang} wpml-ls-current-language menu-item-has-children menu-item-wpml-ls-static"><a href="{current_href}" aria-current="page"><span class="link-before"><img class="wpml-ls-flag" src="{flag_base}{current["flag"]}" alt="{current["name"]}">{current["name"]}<span class="nav-icon-angle">&nbsp;</span></span></a><ul class="sub-menu sub-lv-0">{submenu}</ul></li>'

def ensure_switcher_css(soup: BeautifulSoup, target: Path):
    head = soup.head
    if not head: return
    old = soup.find('style', id='static-wpml-switcher-style')
    if old: old.decompose()
    css = soup.new_tag('style', id='static-wpml-switcher-style')
    css.string = '.wpml-ls-flag{display:inline-block;width:18px;height:12px;margin-right:6px;vertical-align:-1px}.menu-item-wpml-ls-static .sub-menu{min-width:170px}.wpml-ls-item a{white-space:nowrap}'
    head.append(css)

def install_switcher(soup: BeautifulSoup, lang: str, route: str, target: Path):
    remove_existing_switchers(soup)
    flag_base = normalize_asset_url('assets/plugins/sitepress-multilingual-cms/res/flags/', ROOT/'index.html', target, lang)
    if not flag_base.endswith('/'):
        flag_base += '/'
    item_html = make_lang_item(lang, route, target, flag_base)
    for ul in soup.find_all('ul', id=re.compile('menu-main')):
        frag = BeautifulSoup(item_html, 'html.parser')
        ul.append(frag.li)
    ensure_switcher_css(soup, target)
    # hreflang alternates
    if soup.head:
        for link in soup.head.find_all('link', rel='alternate', hreflang=True):
            link.decompose()
        for code in LANGS:
            link = soup.new_tag('link', rel='alternate', hreflang=code, href=rel_url(target, code, route))
            soup.head.append(link)

TITLE_MAP = {
    'nl': {'Home':'Home','Over Ons':'Over Ons','Referenties':'Referenties','References':'Referenties','Links':'Links'},
    'en': {'Home':'Home','Over Ons':'About Us','Referenties':'References','References':'References','Links':'Links'},
    'de': {'Home':'Startseite','Over Ons':'Über uns','Referenties':'Referenzen','References':'Referenzen','Links':'Links'},
    'es': {'Home':'Inicio','Over Ons':'Sobre Nosotros','Referenties':'Referencias','References':'Referencias','Links':'Enlaces'},
}

def local_menu_text(soup: BeautifulSoup, lang: str):
    for a in soup.select('ul.primary-menu-ul a'):
        txt = a.get_text(strip=True)
        if txt in TITLE_MAP['nl'] or txt in TITLE_MAP['en']:
            mapped = TITLE_MAP.get(lang, {}).get(txt)
            if mapped:
                span = a.find('span', class_='link-before')
                if span:
                    # Preserve child images for language items only.
                    if not span.find('img'):
                        span.string = mapped

add_flag_files()
for lang in ['en','de','es']:
    for route in BASE_ROUTES:
        src = SOURCE_FILES[route]
        if not src.exists():
            print('missing source', route)
            continue
        target = target_file(lang, route)
        target.parent.mkdir(parents=True, exist_ok=True)
        html = src.read_text(encoding='utf-8')
        soup = BeautifulSoup(html, 'lxml')
        update_urls(soup, src, target, lang)
        translate_soup(soup, lang)
        local_menu_text(soup, lang)
        install_switcher(soup, lang, route, target)
        target.write_text(str(soup), encoding='utf-8', newline='')
        print('wrote', target.relative_to(ROOT))
# Update NL switchers and internal URLs lightly.
for route in BASE_ROUTES:
    path = SOURCE_FILES[route]
    if not path.exists(): continue
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'lxml')
    update_urls(soup, path, path, 'nl')
    local_menu_text(soup, 'nl')
    install_switcher(soup, 'nl', route, path)
    if soup.html: soup.html['lang'] = 'nl'
    path.write_text(str(soup), encoding='utf-8', newline='')
    print('updated nl', path.relative_to(ROOT))
CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
print('cache entries', len(cache))
