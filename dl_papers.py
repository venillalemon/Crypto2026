#!/usr/bin/env python3
"""Sequential, rate-limit-respecting downloader for eprint PDFs."""
import json, os, re, subprocess, time, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open('current.json'))
want = {6,9,12,16,20,24,35,36,39,40,43,44,47,48,55,56,60,62}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# papers with no eprint link in the program JSON, found manually
SUPPLEMENT = {
    865: "https://eprint.iacr.org/2026/279",   # Careful with the Ring! (earlier title)
    751: "https://eprint.iacr.org/2026/1683",  # Fully-Succinct Multi-Key FHE
    799: "https://eprint.iacr.org/2026/1686",  # Unifying Umbrella Circular-Secure
    383: "https://eprint.iacr.org/2026/1730",  # Fast and Shallow FHE Bootstrapping
}

def slug(s, n=50):
    s = re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-')
    return s[:n].rstrip('-')

jobs = []
for day in d['days']:
    for ts in day['timeslots']:
        for ss in ts['sessions']:
            sid = ss.get('id', '')
            num = int(sid.split('-')[1]) if '-' in sid else -1
            if num not in want:
                continue
            sdir = f"session-{num:02d}-{slug(ss['session_title'],40)}"
            for t in ss.get('talks') or []:
                ep = t.get('eprint') or SUPPLEMENT.get(t['paperId'])
                if not ep:
                    continue
                path = f"paper/{sdir}/{t['paperId']}-{slug(t['title'])}.pdf"
                if os.path.exists(path) and os.path.getsize(path) > 10000:
                    continue
                os.makedirs(os.path.dirname(path), exist_ok=True)
                jobs.append((ep.rstrip('/') + '.pdf', path))

def probe():
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                        "-A", UA, "https://eprint.iacr.org/2026/953.pdf"],
                       capture_output=True, text=True)
    return r.stdout.strip()

# single probe — caller is responsible for waiting quietly beforehand
code = probe()
print(f"probe: {code}", flush=True)
if code != "200":
    print("DONE. still rate limited"); sys.exit(2)

print(f"{len(jobs)} papers to fetch", flush=True)
fails = []
for i, (url, path) in enumerate(jobs):
    ok = False
    for attempt in range(5):
        r = subprocess.run(["curl", "-sL", "-A", UA, "-o", path, "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        code = r.stdout.strip()
        if code == "200" and os.path.exists(path) and os.path.getsize(path) > 10000:
            ok = True
            break
        if code == "429":
            time.sleep(120 * (attempt + 1))
        else:
            time.sleep(10)
    if not ok:
        fails.append(f"{code} {url} -> {path}")
        if os.path.exists(path):
            os.remove(path)
    print(f"[{i+1}/{len(jobs)}] {'ok' if ok else 'FAIL'} {url}", flush=True)
    time.sleep(10)
print("DONE. fails:", len(fails), flush=True)
print("\n".join(fails))
