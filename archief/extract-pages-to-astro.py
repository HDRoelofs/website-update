from __future__ import annotations

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse, urljoin
import json
import posixpath
import re


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "data" / "pages.json"
SKIP_DIRS = {
    ".git",
    ".astro",
    ".github",
    "archief",
    "assets",
    "node_modules",
    "public",
    "site-includes",
    "src",
    "dist",
}


def route_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel.as_posix() == "index.html":
        return ""
    return rel.parent.as_posix()


def route_depth(route: str) -> int:
    return 0 if not route else len(route.split("/"))


def title_for(soup: BeautifulSoup, route: str) -> str:
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        title = re.sub(r"\s+[–-]\s+LE-Network\s*$", "", title).strip()
        if title:
            return title
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)
    h2 = soup.find("h2")
    if h2:
        return h2.get_text(" ", strip=True)
    return "LE-Network" if not route else route.split("/")[-1].replace("-", " ").title()


def description_for(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"].strip()
    text = soup.get_text(" ", strip=True)
    return text[:155] if text else "Samenwerken om leerprocessen te verbeteren."


def normalize_url(value: str, route: str) -> str:
    value = value.strip()
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return value

    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        if parsed.netloc in ("le-network.nl", "www.le-network.nl"):
            path = parsed.path or "/"
            return path if not parsed.fragment else f"{path}#{parsed.fragment}"
        return value

    if value.startswith("/"):
        return value

    base = "/" + (route + "/" if route else "")
    joined = urljoin(base, value)
    path = urlparse(joined).path
    if path.startswith("/assets/") or path.startswith("/site-includes/"):
        return path
    if "." in posixpath.basename(path):
        return path
    if not path.endswith("/"):
        path += "/"
    return path


def normalize_srcset(value: str, route: str) -> str:
    parts = []
    for item in value.split(","):
        bits = item.strip().split()
        if not bits:
            continue
        bits[0] = normalize_url(bits[0], route)
        parts.append(" ".join(bits))
    return ", ".join(parts)


def clean_content(soup: BeautifulSoup, route: str) -> str:
    container = soup.select_one(".entry-content")
    if not container:
        container = soup.select_one("main")
    if not container:
        container = soup.body or soup

    fragment = BeautifulSoup("".join(str(child) for child in container.children), "html.parser")

    for tag in fragment.find_all(["script", "style", "noscript"]):
        tag.decompose()

    for tag in fragment.find_all(True):
        for attr in ("src", "href", "poster", "data-src", "data-lazy-src"):
            if tag.has_attr(attr):
                tag[attr] = normalize_url(tag[attr], route)
        for attr in ("srcset", "data-srcset"):
            if tag.has_attr(attr):
                tag[attr] = normalize_srcset(tag[attr], route)
        if tag.name == "iframe":
            tag["loading"] = "lazy"
        if tag.name == "img":
            tag["loading"] = "lazy"

    return str(fragment)


def collect_pages() -> list[dict]:
    pages = []
    for path in sorted(ROOT.rglob("index.html")):
        rel_parts = path.relative_to(ROOT).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        route = route_for(path)
        html = path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html, "lxml")
        pages.append(
            {
                "route": route,
                "title": title_for(soup, route),
                "description": description_for(soup),
                "content": clean_content(soup, route),
            }
        )
    pages.sort(key=lambda page: (route_depth(page["route"]), page["route"]))
    return pages


pages = collect_pages()
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {len(pages)} pages to {OUT.relative_to(ROOT)}")
for page in pages:
    print(page["route"] or "/")
