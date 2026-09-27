# Crypto2026 — project instructions (loaded every session)

Tutorial notes in Simplified Chinese for selected CRYPTO 2026 papers. The user is a cryptography researcher who cares about **precision** above everything: a wrong number, a made-up attribution, or a reused symbol is worse than saying less. Two modes of work:

- **Mode A — writing notes** → load the skill `crypto-conf-tutorials` (the full pipeline and writing standard live there).
- **Mode B — answering questions about a paper or a note** → rules in this file; no skill needed. This is the default mode of a session.

## Layout

| Path | Content |
|---|---|
| `current.json`, `classification.json`, `sessions.txt` | CRYPTO 2026 program, the 69-paper classification, the confirmed review table (session → paper → L1/L2). `sessions.txt` is authoritative for levels. |
| `paper/session-{NN}-{slug}/{paperId}-{slug}.pdf` | paper PDFs (gitignored) |
| `slides/session-{NN}-{slug}/{paperId}-{slug}.{pdf,pptx}` | slides (gitignored) |
| `notes/L{1,2}/{paperId}-{slug}.md` | one note per paper |
| `notes/L{1,2}/{paperId}/*.png` | that note's figures |
| `dl_papers.py` | ePrint downloader |
| `.claude/skills/crypto-conf-tutorials/` | writing pipeline + `scripts/check_note.py` |

`paperId` is the key for everything: `ls paper/session-*/{id}-*.pdf slides/session-*/{id}-* notes/L*/{id}-*.md`.
Text extraction: `pdftotext -layout <pdf> <scratchpad>/<id>-paper.txt`; for `.pptx`, unzip and pull `<a:t>` runs from `ppt/slides/slide*.xml` (no LibreOffice on this machine).

## Precision rules (both modes)

- **Every number, bound, constant and attribution comes from the paper or slides, or from a computation I actually ran.** If the paper does not state it, say 定性描述 / "论文没给". Never fabricate URLs; a slides URL is used only after `curl -sI` returns 200.
- **Distinguish "论文说的" from "我推的/我算的".** When I verify an identity by computation, say so. When the paper and the slides disagree, or a stated identity fails to check, report it explicitly instead of silently fixing it.
- **Terminology: do not translate common technical terms.** Write bit, trapdoor, lattice, basis, commitment, soundness, PRF, genus, isogeny… in English inside Chinese prose; 如果感觉难翻译就不翻译. The term being defined in a definition is given in English only, never as a "中文 (English)" pair. Translate only fully standard Chinese (公钥、签名、多项式时间). Use the paper's notation unless it collides.
- **Symbol discipline: one letter, one role, per document.** Introduce every symbol at or right before first use. Not even different subscript shapes may reuse a base letter for a different role. If the paper's own notation collides after simplification, rename consistently and say so once.
- **Formula-first.** Definitions, constructions, results and answers are displayed math or theorem statements with a one-line lead-in. Long prose is a smell.

## Mode B — answering questions

- **Audience is the user, a researcher.** Lead with the answer. Terse. No tutorial padding, no background they already have. A displayed formula beats a paragraph.
- **Ground every claim.** Cite the paper (section / theorem / algorithm / page) or the note (§). Before answering anything that depends on details, extract the paper text into the scratchpad and read the relevant part; do not answer from memory of the note alone. Read the slides too when the question is about the authors' intuition.
- **Use the note's notation.** If the note renamed a symbol, say the paper's original name once.
- **Questions that expose a gap in a note** (a "为什么?" the note should have answered, an unstated premise, a wrong or unsourced number): answer first, then propose the patch in one line (which §, what changes) and apply it as a minimal `Edit`. Do not rewrite sections. Keep symbol discipline and the level's word budget; run `python3 .claude/skills/crypto-conf-tutorials/scripts/check_note.py <note>` afterwards.
- **Explicit change requests to a note inside a question**: apply them directly, same minimal-edit rule. If the requested change contradicts the paper, say so with the citation before touching the file, then follow the user's decision.
- **Do not switch into Mode A** (re-reading everything, rewriting the note) unless the user asks for a rewrite.

## Git

- Commit only when asked. Plain summary message; end with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Never push unless asked.
