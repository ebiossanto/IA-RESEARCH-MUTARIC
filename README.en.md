# ricemotions — emotion written in pixels

> English version. The full documentation (`docs/`) is in Portuguese.

The bridge between the **TEOA** project (*Theory of the Artificial Optimal State* —
**why** and **when** an emotion arises) and the **PIXEL/RIC** project (a *relational
incidence code* read from **pixels** — **what** can be recovered from a state that has
been written as an image).

```
episode (6 channels × 32 steps)      TEOA side: state, distance to target s*
   → valence v and activation act     affect():  v = β·L − α·(D_post − d_ref)
   → glyph 48 × 32 pixels             four bands: level | polarity | body | payload
   → read back by the RIC reader      correlations → graphs → nearest-incidence decoding
   → family · provenance · payload    6 classes, 3 provenances, 5.36 bits per glyph
```

**Status: exploratory prototype.** The four experiments (E1–E4) run deterministically
and are covered by smoke tests, but the affective world is **hand-scripted**
(`mundo.py` writes the provenances as scenarios) and the reader **re-reads what the
writer stored literally**. Read `docs/02_analise_achados.md` before quoting any
number — it lists what the results do **not** support.

## Repository layout

```
README.md / README.en.md     this file / Portuguese version
requirements.txt .gitignore  numpy, scipy, matplotlib
run_all.py                   entry point: tests + experiments
ricemotions/
  mundo.py                   TEOA side: episodes, valence, labels   (no I/O)
  glifo.py                   PIXEL/RIC side: write, read, graphs     (no I/O)
  experimentos.py            E1–E4, figures, the only module with I/O
tests/test_smoke.py          contracts + regression of published numbers
docs/                        architecture · findings · TEOA↔PIXEL bridge · roadmap
figs/  resultados/           generated figures and results.json
```

## Running

```bash
pip install -r requirements.txt
python run_all.py --so-testes    # 14 sanity tests (seconds)
python run_all.py                # tests + E1–E4 + figures (a few minutes)
```

Outputs: `figs/{glifos,grafos_prototipo,robustez,carga}.png` and
`resultados/resultados.json`.

## Headline results (balanced accuracy, 1800-glyph test set)

| method | clean | noise σ=0.10 | brightness | row permutation |
|---|---|---|---|---|
| relational (RIC graph) | 0.919 | **0.334** | 0.919 | 0.193 |
| baseline `level+delta` | **1.000** | **1,000** | 0.998 | 0.294 |
| payload, 5.36 bits | 1.000 | 1.000 | 1.000 | 0.117 → **1.000**\* |

\* with `codebook_up_to_isomorphism()`; the previously published 0.208 was an artifact
of collisions between isomorphic words (see findings A3).

τ = 0.7 is selected on the **validation** split; train/val/test come from seeds
1/2/3; 2400/900/1800 glyphs.

## Key findings (details in `docs/02_analise_achados.md`)

1. **The relational code does not beat trivial baselines.** `level+delta` reaches
   1.000 on clean data; the relational reader reaches 0.919. Its real advantage is
   **affine invariance** (per-line gain/offset leaves it at 0.919 while the level
   baseline drops to 0.51).
2. **It collapses under noise** (0.334 = chance at σ=0.10) because edges are hard-
   thresholded at a fixed τ and Hamming decoding has no error correction.
3. **Bug found and fixed:** payload decoding under vertex permutation collided on
   isomorphic words (0.146–0.208 measured; 1.000 with one word per isomorphism
   class). There are exactly 11 classes = integer partitions of 6 → theoretical cap
   `log₂(11) = 3.46` bits.
4. **Family-by-polarity is a copied label**, not an emergent reading (always 1.000).
5. **Canonicalising the body *hurts*** (0.919 → 0.666): searching 720 permutations
   multiplies false matches.
6. **The "alphabet" is a 1-NN classifier** and the provenance is a scripted
   scenario — the claim must be phrased as pattern recognition, not emergence.
7. **Valence dead zone:** all 25/1800 inconsistencies are joy with `v ≈ −0.075`;
   sadness is always negative. A neutral band is needed.
8. Portability issues on Windows (cp1252 vs `σ`), non-importable package name and
   missing tests — all fixed in this reorganisation.

## Limitations

- No agent: nothing is *chosen*; no action, cost or decision.
- No feedback: reading a glyph does not change the reader or the world.
- No memory across glyphs; TEOA's cycles and hysteresis are not modelled here.
- The real `teoa/core.py` is **not** used; `mundo.py` is a scripted stand-in.
- Exploratory: hyper-parameters were chosen by us; no pre-registration, no
  hypothesis test yet.

## Next steps

See `docs/04_plano_desenvolvimento.md` (P0–P3, each with acceptance criteria):
isomorphism-aware payload in E3 (P0.2), soft edge decoding for noise robustness
(P0.3), accuracy-vs-σ curves (P0.4), real baselines + bootstrap hypothesis tests
(P1), then wiring the actual TEOA core and a two-agent communication loop (P2).

## Relation to the TEOA project

Local: `Desktop/Emoções/` (see its `README.md` and `docs/`). The conceptual mapping
between TEOA concepts, this code and the RIC/PIXEL reading model — plus the seven
open gaps — is documented in `docs/03_relacao_pixel_teoa.md`.
