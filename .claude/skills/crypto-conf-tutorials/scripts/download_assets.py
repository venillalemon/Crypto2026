#!/usr/bin/env python3
"""Download paper PDFs and slides for every Level-1/Level-2 paper in a
manifest.json produced by fetch_program.py.

Strategy per paper (best-effort, failures are recorded, not fatal):
  paper.pdf : eprint link from manifest -> its /paper.pdf form
              else ePrint full-text search by title
              else any direct .pdf "paper" link from the program
              (Springer/DOI links are usually paywalled -> recorded as a miss)
  slides.pdf: the program's slides link, if present.

Layout:  <papers-dir>/L{1,2}/{id:03d}-{slug}/{paper.pdf, slides.pdf, meta.json}

Usage:
  python download_assets.py work/manifest.json --papers-dir work/papers
  python download_assets.py work/manifest.json --only 12,17   # re-try specific ids
"""
import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (compatible; conf-tutorial/1.0)"}
DELAY = 1.0  # seconds between HTTP requests: be polite to iacr.org


def http_get(url: str, timeout=60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def save(url: str, dest: Path) -> str:
    """Download url to dest if it looks like a PDF. Returns status string."""
    if dest.exists() and dest.stat().st_size > 10_000:
        return "exists"
    time.sleep(DELAY)
    data = http_get(url)
    if not data.startswith(b"%PDF"):
        return f"not-a-pdf ({len(data)} bytes from {url})"
    dest.write_bytes(data)
    return f"ok ({len(data)//1024} KB)"


def norm_title(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def eprint_pdf_url(link: str) -> str:
    """https://eprint.iacr.org/2026/123[.pdf] -> https://eprint.iacr.org/2026/123.pdf"""
    m = re.search(r"eprint\.iacr\.org/(\d{4}/\d+)", link)
    return f"https://eprint.iacr.org/{m.group(1)}.pdf" if m else ""


def eprint_search(title: str) -> str:
    """Search ePrint by title; return the report's pdf URL if a result's title
    matches closely, else ''. Parses the search page defensively."""
    q = urllib.parse.quote(title)
    try:
        time.sleep(DELAY)
        html = http_get(f"https://eprint.iacr.org/search?q={q}").decode(
            "utf-8", errors="replace")
    except Exception as e:
        print(f"    eprint search failed: {e}", file=sys.stderr)
        return ""
    want = norm_title(title)
    # candidate report ids in order of appearance
    for rid in dict.fromkeys(re.findall(r'href="/(\d{4}/\d+)"', html)):
        # grab a window of page text after this link and compare titles
        i = html.find(f'href="/{rid}"')
        window = re.sub(r"<[^>]+>", " ", html[i: i + 1200])
        if want and want[: max(20, len(want) // 2)] in norm_title(window):
            return f"https://eprint.iacr.org/{rid}.pdf"
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--papers-dir", default=None,
                    help="default: <manifest dir>/papers")
    ap.add_argument("--only", default="",
                    help="comma-separated paper ids to (re)download")
    args = ap.parse_args()

    mpath = Path(args.manifest)
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    pdir = Path(args.papers_dir) if args.papers_dir else mpath.parent / "papers"
    only = {int(x) for x in args.only.split(",") if x.strip()}

    report = []
    for p in manifest["papers"]:
        if p["level"] not in (1, 2):
            continue
        if only and p["id"] not in only:
            continue
        d = pdir / f"L{p['level']}" / f"{p['id']:03d}-{p['slug']}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "meta.json").write_text(
            json.dumps(p, indent=1, ensure_ascii=False), encoding="utf-8")
        entry = {"id": p["id"], "title": p["title"], "dir": str(d),
                 "paper": "", "slides": ""}
        print(f"[{p['id']:03d}] {p['title'][:70]}")

        # ---- paper.pdf ----
        links = p.get("links", {})
        tried = []
        candidates = []
        if links.get("eprint"):
            candidates.append(eprint_pdf_url(links["eprint"]))
        for u in [links.get("paper")] + links.get("other", []):
            if u and u.lower().endswith(".pdf"):
                candidates.append(u)
        for url in [c for c in candidates if c]:
            try:
                entry["paper"] = save(url, d / "paper.pdf")
                if entry["paper"].startswith(("ok", "exists")):
                    break
                tried.append(entry["paper"])
            except Exception as e:
                tried.append(f"{url}: {e}")
        if not entry["paper"].startswith(("ok", "exists")):
            url = eprint_search(p["title"])
            if url:
                try:
                    entry["paper"] = save(url, d / "paper.pdf") + " [eprint-search]"
                except Exception as e:
                    tried.append(f"{url}: {e}")
        if not entry["paper"].startswith(("ok", "exists")):
            entry["paper"] = "MISSING | tried: " + ("; ".join(tried) or "no links")
        print(f"    paper : {entry['paper']}")

        # ---- slides.pdf ----
        if links.get("slides"):
            try:
                entry["slides"] = save(links["slides"], d / "slides.pdf")
            except Exception as e:
                entry["slides"] = f"failed: {e}"
        else:
            entry["slides"] = "no slides link in program"
        print(f"    slides: {entry['slides']}")
        report.append(entry)

    rpath = pdir / "download_report.json"
    rpath.write_text(json.dumps(report, indent=1, ensure_ascii=False),
                     encoding="utf-8")
    missing = [e for e in report if e["paper"].startswith("MISSING")]
    print(f"\nDone: {len(report)} papers, {len(missing)} missing PDFs "
          f"-> see {rpath}")
    for e in missing:
        print(f"  MISSING #{e['id']}: {e['title'][:70]}")


if __name__ == "__main__":
    main()
