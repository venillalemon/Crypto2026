---
name: conf-paper-tutorials
description: Scrape an IACR conference program (CRYPTO / Eurocrypt / Asiacrypt / TCC / PKC, e.g. crypto.iacr.org/2026), download the paper PDFs and slides for selected tracks, and write tutorial notes in Simplified Chinese as Markdown files (with extracted figures) at two depth levels. Use whenever the user mentions an IACR conference program URL, asks to fetch conference papers and slides, or wants 论文导读/教程/介绍文章 written from conference papers for crypto beginners — even if they only mention part of the pipeline (e.g. just "抓取 CRYPTO 的论文" or just "把这些论文写成导读").
---

# Conference Paper Tutorials (会议论文导读)

Pipeline: fetch program → classify papers into two tutorial levels → download PDFs & slides → write one Markdown note per paper (figures extracted alongside) → build an index page.

The reader is a **lower-year undergraduate who has just started cryptography** (知道 lattice 全部基础知识、知道密码学基础 PRG、PRF、MAC、Hash、加密、签名、zkp 的基础概念，知道初等数论和抽象代数、Galois理论、但没上过研究生课程). The user commissioning the articles is a cryptography researcher who cares about **precision**: wrong notation or invented numbers is worse than saying less.

## Step 0 — Environment

Scripts need only Python 3 stdlib. Reading PDFs needs `pdftotext` (`poppler-utils`) or `pip install pypdf`. Work in a project directory, e.g. `crypto2026/`.

## Step 1 — Fetch & classify the program

IACR conference sites render `program.php` client-side from `<base-url>/json/program.json` (schema: `days → timeslots → sessions → talks`). Do NOT scrape the HTML — fetch the JSON:

```bash
python scripts/fetch_program.py --base-url https://crypto.iacr.org/2026 --out crypto2026/
```

This writes `program.json`, `manifest.json`, and `sessions.txt` (a review table: every session, every paper, its assigned level and the rule that matched).

**Show the classification table to the user and get confirmation before downloading.** The keyword rules are heuristics; session names vary by year and papers can straddle areas. Fix misclassifications with an overrides file, then re-run:

```json
// overrides.json — case-insensitive substring of paper or session title
{ "watermark": 0, "Threshold ML-DSA": 1 }
```
```bash
python scripts/fetch_program.py --base-url ... --out crypto2026/ --overrides overrides.json
```

If the user restricts scope further (specific days/sessions), set everything else to 0 via overrides.

### Classification rules (precedence matters — specific before general)

| Priority | Topic | Level |
|---|---|---|
| 1 | code-based PQC; isogeny-based PQC | **1** |
| 2 | quantum *cryptography* (constructions: unclonable crypto, quantum money, QKD, one-shot signatures…) | **1** |
| 3 | lattices & lattice cryptanalysis (LWE/SIS/NTRU, sieving, BKZ…) | **2** |
| 4 | quantum *algorithms* / quantum cryptanalysis | **2** |
| 5 | other post-quantum crypto (ML-DSA/ML-KEM, hash-based sigs, general PQC) | **2** |
| 6 | foundations; FHE; MPC & garbling; threshold cryptography; proof systems / ZK / SNARKs; consensus | **1** |
| 7 | everything else (symmetric-key cryptanalysis, side channels, real-world, …) | **skip** |

The carve-outs exist because "PQC" broadly is Level 2 but its code-based and isogeny-based sub-areas are Level 1, and quantum *cryptography* (building things) is Level 1 while quantum *algorithms* (breaking things) is Level 2. When a paper genuinely straddles (e.g. lattice-based threshold signatures), classify by what the paper's *contribution* is about — read the abstract if unsure, and flag it to the user in the review table discussion.

## Step 2 — Download PDFs and slides

```bash
python scripts/download_assets.py crypto2026/manifest.json
```

Layout: `crypto2026/papers/L{1,2}/{id}-{slug}/{paper.pdf, slides.pdf, meta.json}` plus `download_report.json`. The script prefers ePrint (Springer links are paywalled), falls back to ePrint full-text search by title, and records misses instead of failing.

For each `MISSING` paper: web-search `"<exact title>" eprint` or the authors' pages, download manually with `curl -A "Mozilla/5.0" -o paper.pdf <url>`, or tell the user which papers you could not obtain (they attended the conference and may have access). Retry specific papers with `--only 12,17`. Slides appear on the program gradually after the conference — mention that re-running later may pick up more.

## Step 3 — Write the articles

**Read before writing.** For each paper: extract the PDF text (`pdftotext -layout paper.pdf -`), and read the slides if present — slides give the authors' own simplification and the best "why it works" narrative. Base every claim, number, and attribution **only on the paper/slides** (plus what you can verify). Never invent bounds, constants, or prior-work numbers; if the paper doesn't state a number, write 定性描述 instead. This is the user's hardest requirement.

Language & precision:

- 简体中文 prose, tutorial register.
- **Terminology (user preference, 2026-09): do NOT translate common technical terms.** Write bit, trapdoor, lattice, basis, malicious, syndrome, decoder, commitment, soundness, PRF, … directly in English inside the Chinese prose. Rule of thumb: 如果感觉难翻译就不翻译 — a forced Chinese coinage is worse than the English word. In particular, **the term being defined in a definition is a noun — give it in English only**, never "中文 (English)" pairs (write "**parity-check matrix** \(\mathbf{H}\) 满足…", not "校验矩阵 (parity-check matrix)"). Translate only when the Chinese term is fully standard and reads naturally (公钥、签名、多项式时间). Use standard notation exactly as the paper does.
- **Formula-first (user preference, 2026-09): 能用公式说清楚的,就不要写大段文字。** State definitions, constructions and results as displayed formulas / theorem statements with a short lead-in sentence, not as paragraphs paraphrasing them. Long prose blocks are a smell.
- **Formulas must be self-contained, with clean symbol discipline (user preference, 2026-09).** The reader must be able to name every symbol in a formula without hunting: introduce each symbol at or immediately before its first use. **Never assign one letter two roles anywhere in the same note** — not even via different subscript shapes (a letter indexing one thing may not reappear indexing another, and a base letter may not carry two different subscript conventions). If the paper's own notation collides after simplification, rename consistently and say so once.
- **Self-containedness extends to reasoning, not just symbols (user preference, 2026-09).** Apply the reader test at every step: whatever a sharp reader would ask "为什么?" about must be answered inline, at the point of use. Two recurring cases: (a) a formula whose *reading* is non-obvious — unusual convention, integer vs field arithmetic, a transpose/aggregation direction, an inner product whose two operands play different roles — gets one or two interpretive sentences right after it (what each side is, what the result *means*); (b) a premise the whole argument stands on (e.g. "a decoding failure leaks key material", "this oracle access breaks the scheme") counts as 基础知识: sketch its mechanism in a few lines instead of citing it as a black box.
- **Rigor is level-independent (user preference, 2026-09).** 无论 L1 还是 L2:核心动机、idea、算法、逻辑链条都必须完整、严密地讲清楚 — the levels differ only in how much proof detail is carried (see below), never in rigor or in whether the mechanism is actually explained.
- **Figures (user preference, 2026-09): figures must illustrate the idea or the algorithm, never benchmark/experiment results.** Pick the paper's or slides' mechanism illustrations — the pictures the authors drew to explain how the scheme works (these are the reader's memory anchors). Performance/experiments get at most a brief mention in prose; do not spend a figure on result plots or timing tables. Extract with `pdftoppm -png -r 150 -f <page> -l <page> -x -y -W -H` (crop to content), save as PNG files under the note's image directory (see Output below), reference with relative Markdown image links, and walk through each figure in the text.
- Explain operationally first (输入是什么、输出是什么、谁在和谁交互), intuition second, algebra last.

### Level 1 — 入门导读 (~1500–3000 汉字, formula-first so word count stays modest)

**Redefined per user (2026-09): L1 omits only the HEAVY proofs.** L1 is NOT a hand-wavy "what and why" piece. It must:

- **state the core theorems** — the paper's main theorem(s) written out precisely (displayed statement with the actual quantifiers/bounds), complex proofs omitted;
- **include every proof that is simple algebra** (user, 2026-09: 如果 proof 是很简单的代数,那必须要讲) — a two-line computation, an identity, a counting argument belongs in L1; what gets dropped is the heavy machinery (security reductions, hybrid arguments, concentration analyses);
- **give the construction / 做法** — the actual scheme or algorithm (algorithm blocks welcome), and the key idea behind why it works;
- **be self-contained** — define every object the theorem statements use, including standard background (tersely, formula-style; the L2 "skip basics" preference does NOT apply to L1, because self-containedness wins there);
- use the paper's mechanism figure(s).

What separates L1 from L2 is exactly one thing: **L1 carries only the easy proofs; L2 carries them all.** Rigor, motivation, idea, algorithm and logic are identical requirements at both levels.

Sections (use `§1` numbering):

1. **研究什么** — precise problem setup with the definitions needed downstream.
2. **为什么研究它** — real stakes, prior state in brief.
3. **核心定理与做法** — main theorem statements + the construction + idea + the simple-algebra proofs. This section carries the note.
4. **一句话带走** — closing box.

### Level 2 — 深入解析 (~3500–6500 汉字)

Focus: **算法与 idea 的细节、为什么能 work、既往成果、量化提升**。 Sections:

**User preference (confirmed 2026-08):** L2 articles may run longer than the original 2500–4500 target — up to ~6500 汉字 is welcome when the extra length goes into prior work, comparisons, and detailed derivations (not into background). Additionally: skip lattice-related basics entirely — no term cards or definitions for 格/lattice, SIS/LWE, 离散高斯, GSO, Babai, q-ary lattices, trapdoor bases and the like; assume the reader already has them. Reallocate those words to §2 此前的成果, §4 为什么能 work (detailed idea 阐述与推导), and the "本文哪里好" comparison — these three carry the article.

1. **背景与问题设定** — precise definitions and notation (small notation table if ≥4 symbols recur); state the exact problem (e.g. SIS∞ with which parameters). Keep this section short; per the preference above, do not re-teach standard lattice background — only pin down the paper-specific setup and notation.
2. **此前的成果** — the line of prior work with concrete numbers/bounds and attributions (author-year), taken from the paper's own related-work/comparison; enough that the reader sees the gap.
3. **本文的算法** — step-by-step in `.algo` boxes with explicit 输入/输出; decompose multi-phase algorithms into one box per phase, prose between boxes explaining the role of each phase.
4. **为什么能 work** — the key insight first in words, then **actual proofs/derivations, not just sketches** (user preference, 2026-09: L2 是需要 prove 的层级): derive the central bounds/equations step by step as displayed math, show which lemma does the heavy lifting, where the previous approach's obstacle was and how it's circumvented. Formula-first — a chain of displayed equations with one-line justifications beats paragraphs describing the proof. This section is the heart.
5. **提升了多少** — a `.compare` table: prior works vs this work, asymptotics and/or concrete numbers, `this-work` row highlighted; note caveats (different models, assumptions) honestly.
6. **局限与延伸阅读** — what's open; 2–4 pointers (ePrint links) for going deeper.

### Output format — Markdown (user preference, 2026-09; replaces the earlier HTML pipeline)

Each note is a **Markdown file**, not HTML (the `assets/*.html` templates and the 2026-08 dark-theme preference applied to the retired HTML pipeline; they are kept only for reference). Conventions:

- Path: `notes/L{1,2}/{paperId}-{slug}.md`; extracted figure PNGs go in the sibling directory `notes/L{1,2}/{paperId}/` and are referenced relatively (`![…]({paperId}/fig-name.png)`).
- Math in `$…$` / `$$…$$`. Header: 中文标题 (faithful translation, not clickbait) as `#`, original English title + authors + session on the lines below; footer links to ePrint and slides (omit links you don't have — never fabricate URLs).
- Algorithm blocks as bold-labelled lists or fenced blocks; theorem statements as blockquotes with a bold label (**定理 (informal)** / paper's numbering); comparison tables as Markdown tables.

Write notes one at a time, fully; for large batches, confirm the first one or two with the user before continuing (风格确认成本远低于返工).

## Step 4 — Index page

Write `notes/index.md`: group by Level then by session, one entry per note with 中文标题、英文原题、authors、a one-line hook you write. Verify every relative link resolves.

## Done checklist

- [ ] sessions.txt reviewed & classification confirmed by user
- [ ] download_report.json misses handled or reported
- [ ] every note: numbers traceable to the paper; symbols all defined, no letter reused; figures illustrate ideas (not experiment results); math delimiters balanced
- [ ] index.md links all notes, no dead links
