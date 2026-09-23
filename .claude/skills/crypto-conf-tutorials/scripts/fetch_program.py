#!/usr/bin/env python3
"""Fetch an IACR conference program (json/program.json), extract all talks,
classify each into tutorial Level 1 / Level 2 / skip, and emit a manifest.

IACR conference sites (crypto/eurocrypt/asiacrypt/tcc/pkc .iacr.org) render
program.php client-side from  <base-url>/json/program.json  with schema:
    { "days": [ { "date", "timeslots": [ { "starttime", "endtime",
        "sessions": [ { <session title key>, "talks": [ {"title", "authors", ...links} ] } ] } ] } ] }
Key names vary slightly between years, so extraction below is defensive.

Usage:
  python fetch_program.py --base-url https://crypto.iacr.org/2026 --out work/
  python fetch_program.py --base-url ... --out work/ --list-sessions   # review only
  python fetch_program.py --base-url ... --out work/ --overrides overrides.json

overrides.json (optional):  { "substring of paper or session title": 0 | 1 | 2 }
(0 = skip, 1 = Level 1, 2 = Level 2; case-insensitive substring; wins over rules)
"""
import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (compatible; conf-tutorial/1.0)"}

# ---------------------------------------------------------------------------
# Classification rules. FIRST MATCH WINS, top to bottom — order encodes
# precedence. Rationale: code-based / isogeny-based PQC and *constructive*
# quantum cryptography are Level 1 even though PQC-in-general and quantum
# *algorithms* are Level 2, so the specific rules must come first.
# ---------------------------------------------------------------------------
RULES = [
    # -- Level 1 carve-outs that would otherwise be caught by Level 2 rules --
    (1, "code-based PQC",       ["code-based", "code based", "codes", "decoding",
                                 "mceliece", "syndrome"]),
    (1, "isogeny-based PQC",    ["isogen", "sqisign", "csidh", "supersingular"]),
    (1, "quantum cryptography", ["quantum cryptography", "unclonab", "quantum money",
                                 "quantum key", "qkd", "one-shot signature",
                                 "quantum commitment"]),
    # -- Level 2 --
    (2, "lattice / lattice cryptanalysis",
                                ["lattice", "lwe", "sis", "ntru", "bkz", "siev",
                                 "svp", "cvp", "basis reduction"]),
    (2, "quantum algorithms",   ["quantum algorithm", "quantum attack",
                                 "quantum cryptanalysis", "shor", "grover",
                                 "kuperberg", "dihedral coset"]),
    (2, "post-quantum cryptography",
                                ["post-quantum", "post quantum", "pqc",
                                 "ml-dsa", "ml-kem", "dilithium", "kyber", "falcon",
                                 "sphincs", "hash-based signature", "fips 20"]),
    # -- Level 1 --
    (1, "foundations",          ["foundation", "black-box", "minicrypt", "cryptomania",
                                 "one-way function", "pseudorandom", "prf", "prg",
                                 "obfuscat", "impagliazzo"]),
    (1, "FHE",                  ["fhe", "homomorphic", "bootstrap", "tfhe", "fhew",
                                 "ckks", "bgv", "bfv"]),
    (1, "MPC / garbling",       ["mpc", "multi-party", "multiparty", "secure computation",
                                 "garbl", "oblivious transfer", "ot", "secret sharing",
                                 "spdz", "bmr", "private set intersection", "psi"]),
    (1, "threshold cryptography", ["threshold"]),
    (1, "proof systems",        ["proof system", "snark", "stark", "zero-knowledge",
                                 "zero knowledge", "zk", "argument", "iop",
                                 "lookup", "sumcheck", "succinct", "probabilistic proof"]),
    (1, "consensus",            ["consensus", "byzantine", "blockchain", "agreement",
                                 "broadcast", "state machine replication"]),
]

LEVEL_NAME = {0: "SKIP", 1: "L1", 2: "L2"}


def fetch_json(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"\s+", " ", s).strip().lower()


def slugify(title: str, maxlen: int = 60) -> str:
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:maxlen].rstrip("-") or "untitled"


def get_first(d: dict, keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def extract_authors(talk: dict):
    """Authors may be a string, a list of strings, or a list of dicts."""
    for key in ("authors", "speakers", "speaker", "presenter", "author"):
        v = talk.get(key)
        if not v:
            continue
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            names = []
            for a in v:
                if isinstance(a, str):
                    names.append(a)
                elif isinstance(a, dict):
                    n = get_first(a, ["name", "author", "speaker"])
                    aff = get_first(a, ["affiliation", "aff"])
                    names.append(f"{n} ({aff})" if aff else n)
            return "; ".join(x for x in names if x)
    return ""


URL_RE = re.compile(r"https?://[^\s\"'<>]+")


def collect_links(obj, out, keyhint=""):
    """Recursively collect URLs; use the JSON key name to guess the link type."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            collect_links(v, out, keyhint=str(k).lower())
    elif isinstance(obj, list):
        for v in obj:
            collect_links(v, out, keyhint=keyhint)
    elif isinstance(obj, str):
        for u in URL_RE.findall(obj):
            u = u.rstrip(".,;)")
            lo = u.lower()
            if "eprint.iacr.org" in lo:
                out.setdefault("eprint", u)
            elif "slide" in keyhint or "/slides/" in lo:
                out.setdefault("slides", u)
            elif "video" in keyhint or "youtu" in lo or "video" in lo:
                out.setdefault("video", u)
            elif ("paper" in keyhint or "doi" in lo or "springer" in lo
                  or "cryptodb" in lo or lo.endswith(".pdf")):
                out.setdefault("paper", u)
            else:
                out.setdefault("other", [])
                if u not in out["other"]:
                    out["other"].append(u)


def classify(session_title: str, paper_title: str, overrides: dict):
    """Return (level, reason). Overrides first, then rules on session title,
    then rules on paper title, else skip."""
    for pat, lvl in overrides.items():
        p = norm(pat)
        if p and (p in norm(paper_title) or p in norm(session_title)):
            return int(lvl), f"override: '{pat}'"
    for text, where in ((session_title, "session"), (paper_title, "title")):
        t = norm(text)
        if not t:
            continue
        for lvl, label, kws in RULES:
            for kw in kws:
                # word boundary at the start always; also at the end for short
                # keywords (acronyms like sis/lwe/ot), so 'sis' does not match
                # inside 'cryptanalysis' but longer keywords still act as
                # prefixes ('isogen' -> isogeny/isogenies, 'garbl' -> garbling).
                pat = r"(?<![a-z0-9])" + re.escape(kw)
                if len(kw) <= 4:
                    pat += r"(?![a-z0-9])"
                if re.search(pat, t):
                    return lvl, f"{where} matched '{kw}' ({label})"
    return 0, "no rule matched"


def walk_program(prog: dict):
    """Yield (day, time, session_title, talk_dict)."""
    for day in prog.get("days", []):
        date = day.get("date", "")
        for slot in day.get("timeslots", []):
            t0 = slot.get("starttime", "")
            for sess in slot.get("sessions", []):
                stitle = get_first(sess, ["session_title", "title", "name",
                                          "session", "session_name"])
                talks = None
                for k in ("talks", "presentations", "papers", "items"):
                    if isinstance(sess.get(k), list):
                        talks = sess[k]
                        break
                for talk in (talks or []):
                    if isinstance(talk, dict):
                        yield date, t0, stitle, talk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True,
                    help="e.g. https://crypto.iacr.org/2026 (no trailing slash needed)")
    ap.add_argument("--out", default="work", help="output directory")
    ap.add_argument("--overrides", help="path to overrides.json")
    ap.add_argument("--list-sessions", action="store_true",
                    help="only print the session/classification table")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    overrides = {}
    if args.overrides:
        overrides = json.loads(Path(args.overrides).read_text(encoding="utf-8"))

    url = f"{base}/json/program.json"
    print(f"Fetching {url} ...", file=sys.stderr)
    try:
        prog = fetch_json(url)
    except Exception as e:
        print(f"ERROR fetching program.json: {e}\n"
              f"Inspect the site manually (view-source of program.php) to find "
              f"the JSON it loads, then pass it via --base-url or download it "
              f"yourself to {outdir}/program.json.", file=sys.stderr)
        sys.exit(1)
    (outdir / "program.json").write_text(json.dumps(prog, indent=1), encoding="utf-8")

    papers, seen = [], set()
    for date, t0, stitle, talk in walk_program(prog):
        title = get_first(talk, ["title", "paper_title", "name"])
        if not title:
            continue
        key = norm(title)
        if key in seen:          # same paper can appear twice (e.g. award session)
            continue
        seen.add(key)
        links = {}
        collect_links(talk, links)
        level, reason = classify(stitle, title, overrides)
        papers.append({
            "id": len(papers) + 1,
            "title": title,
            "slug": slugify(title),
            "authors": extract_authors(talk),
            "session": stitle,
            "day": date,
            "time": t0,
            "level": level,
            "reason": reason,
            "links": links,
        })

    if not papers:
        print("WARNING: no talks found — the JSON schema may differ. "
              f"Inspect {outdir}/program.json and adapt walk_program().",
              file=sys.stderr)

    # human-review table
    lines, counts = [], {0: 0, 1: 0, 2: 0}
    cur = None
    for p in sorted(papers, key=lambda x: (x["day"], x["time"], x["session"])):
        head = f"{p['day']} {p['time']}  [{p['session']}]"
        if head != cur:
            lines.append("\n" + head)
            cur = head
        counts[p["level"]] += 1
        lines.append(f"  {LEVEL_NAME[p['level']]:4} #{p['id']:<3} {p['title']}"
                     f"    <- {p['reason']}")
    table = "\n".join(lines)
    (outdir / "sessions.txt").write_text(table, encoding="utf-8")
    print(table)
    print(f"\nTotal: {len(papers)} papers | L1={counts[1]}  L2={counts[2]}  "
          f"skip={counts[0]}")

    if not args.list_sessions:
        (outdir / "manifest.json").write_text(
            json.dumps({"base_url": base, "papers": papers},
                       indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {outdir}/manifest.json — review sessions.txt, fix "
              f"misclassifications via --overrides, then run download_assets.py")


if __name__ == "__main__":
    main()
