# ricemotions — emotion written in pixels

[![CI](https://github.com/ebiossanto/IA-RESEARCH-MUTARIC/actions/workflows/ci.yml/badge.svg)](https://github.com/ebiossanto/IA-RESEARCH-MUTARIC/actions/workflows/ci.yml)

> English version. The full documentation (`docs/`) is in Portuguese — start at
> [`docs/00_indice.md`](docs/00_indice.md) (index) and
> [`docs/07_continuidade.md`](docs/07_continuidade.md) (how to resume the work).

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

**Status: exploratory prototype.** The six experiments (E1–E6), three external
verification runs (E7–E9, from the attached MutaCore document), **E10** (equal
budget, from the MUTARIC ev audit) and **E10b** (strong memory controls, from
the MUTARIC ev 2 audit) run deterministically
and are covered by **32 smoke tests**, but the affective world is **hand-scripted**
(`mundo.py` writes the provenances as scenarios) and the reader **re-reads what the
writer stored literally**. Read `docs/02_analise_achados.md` before quoting any
number — it lists what the results do **not** support.

## Repository layout

```
README.md / README.en.md     this file / Portuguese version
requirements.txt .gitignore  numpy, scipy, matplotlib
run_all.py                   entry point: tests + experiments
.github/workflows/ci.yml     CI: 32 tests on Windows + Linux
ricemotions/
  mundo.py                   TEOA side: episodes, valence, labels   (no I/O)
  glifo.py                   PIXEL/RIC side: write, read, graphs     (no I/O)
  residuo.py                 E5: residue generation/routing, Landauer, τ
  agente.py                  E6: transition + two-way loop (S*, w, τ fed back)
  homeostase.py              MutaCore: endogenous residue, telemetry → S*/τ, policy
  experimentos.py            E1–E10 + E10b, figures, the only module with I/O
tests/test_smoke.py          contracts + regression of published numbers (32)
docs/                        11 documents: index · architecture · findings · bridge · roadmap · residue/agency · MutaCore · continuity · history · MUTARIC ev and ev 2 audits
figs/  resultados/           generated figures and resultados/resultados.json
                             (+ maquina.json and telemetria_real.json: real machine
                             collection, non-deterministic, never regressed)
```

## Running

```bash
pip install -r requirements.txt
python run_all.py --so-testes    # 32 sanity tests (seconds)
python run_all.py                # tests + E1–E10 + E10b + figures (a few minutes)
python -m ricemotions.experimentos --telemetria   # real machine collection (optional,
                                                  # needs psutil; not regressed)
```

Outputs: `figs/{glifos,grafos_prototipo,robustez,carga,curva_sigma,residuo,agencia,mutacore,e10_orcamento,e10b_controles}.png`
and `resultados/resultados.json`; the optional collection writes
`resultados/maquina.json` and `resultados/telemetria_real.json` (non-deterministic).

## Headline results (balanced accuracy, 1800-glyph test set)

| method | clean | noise σ=0.10 | brightness | row permutation |
|---|---|---|---|---|
| relational (RIC graph), hard threshold | 0.919 | **0.334** | 0.919 | 0.193 |
| baseline `level+delta` | **1.000** | **1.000** | 0.998 | 0.294\*\* |
| payload, 5.36 bits | 1.000 | 1.000 | 1.000 | 0.117 → **1.000**\* |
| **robust reader** (σ̂ from R=3 redundancy + attenuation correction + reliability weights) | 0.892 | **0.733** | — | — |

\* with `codebook_up_to_isomorphism()`; the previously published 0.208 was an artifact
of collisions between isomorphic words (see findings A3).
\*\* under permutation what was measured is `delta` alone = 0.294 (and `level` =
0.254); `level+delta` does not run in that condition — the correct table is in
`docs/02` §1.

τ = 0.7 is selected on the **validation** split; train/val/test come from seeds
1/2/3; 2400/900/1800 glyphs.

## New results this cycle (`docs/05`, in Portuguese)

1. **The noise collapse belonged to the threshold, not to the relational code.**
   σ̂ is estimated for free from the glyph's own R=3 redundancy; unreliable pairs are
   *ignored* instead of becoming random bits. Gain over the hard reader: **+0.395 at
   σ=0.10**, **+0.451 at σ=0.15**; at σ=0.40 the hard reader is at chance (0.167)
   while the robust one still scores 0.308.
2. **Residue has three destinations (E5, same residual state):** spread as pixel noise →
   class 0.270 and **0.000 residue recovered**; a dedicated band → 0.933 raw /
   0.977 recovered at a cost of **6 rows**; the **720 symmetries of the canonical
   body** → 0.837 under the canonical reader (the *same* score the band gets when
   read the same way) / **1.000** recovered at a cost of **0 rows**. Read raw, the
   symmetry scores 0.303 — the permutation must be undone. Canonicalising costs
   ~0.10 accuracy (0.933 → 0.837) and buys the *combinatorial ceiling*
   `log₂720 = 9.49` bits — the **order** of the channels, not their amplitudes —
   for free.
3. **Two-way agency (E6):** the read state alters the *transition rules*. Same state,
   different residue history → the next transition differs by **0.00615** when closed
   vs exactly **0.00000** when open. A Landauer-style filter raises tension
   (0.248 → 0.522) and shifts the target `S*` by +0.25, which relaxes back to +0.02
   during rest. Residue-driven τ rises 0.700 → 0.867 and recovers to 0.704.
4. **Exhaustion is measured as lost *gains*:** at τ=0.90 the system picks up **60%
   fewer new relations** under a weak stimulus (0.067 → 0.027) while losing more of
   the ones it had — apathy as an inability to incorporate information, not silence.

## Analysis of the attached MutaCore document (`docs/06`, in Portuguese)

Rule applied: **no claim was accepted without first being reproduced numerically.**
Four mechanisms were adopted (seven code entries — `docs/06` §2); of the 18 claims,
**six failed**, four were partial or unverifiable and eight were confirmed.

| Claim in the document | Verdict | Evidence |
|---|---|---|
| published `R_L` JSON (γ=0.8, α_L=0.15) | **reproduced exactly** | max diff 8.7e-7 (E7) |
| telemetry → `S*` and → `τ`; distance-to-`S*` policy | **correct — adopted** | `homeostase.py`, optional `Agente.passo(carga_hw=)` (default 0 ⇒ published numbers unchanged) |
| low `d_min` payloads collapse at σ=0.40 | **correct** | 0.580 (`d_min=1`) vs 0.927 (`d_min=8`) |
| ~91.8 % robustness under **noise** σ ≤ 0.30 | **false** (true for affine only) | hard reader 0.167 at σ=0.30 = chance; robust reader only 0.391 |
| "level drops, relational holds" under injected residue | **not at γ=0.8** | Δ = +0.006; only from γ×10 (−0.007 vs −0.051) |
| affective robot survives longer (Layer-3 validation) | **measures nothing** | 1000 vs 1000 cycles = 0 %; death is structurally impossible |
| dynamic `S*` = self-preservation | **refuted by ablation** | in a lethal regime it **costs 20.6 cycles**; early recharging gains 36 |
| flux cipher keyed by the residue | **16.61 bits** | brute force recovers the key in ≈0.3 s |

Also: the injected `Φ` has magnitude **0.021** (10.4 % of the script's signal
amplitude) against our own `ΔT = +0.274` in E6, and the snippet the document tells
us to paste into `mundo.py` produces `R_L ≡ 0` by construction (`docs/06` §8.1).

## Second external audit — "MUTARIC ev" (`docs/09`, in Portuguese)

Same rule: **nothing accepted without numerical reproduction.** All five
corrections were adopted — two wordings ("same energy" → "three codifications of
the same residual state"; `log₂720` stated as a combinatorial ceiling, not usable
capacity), one marker (`E9` now declares `campos_nao_deterministicos:
["segundos"]`), and two became roadmap items (**P1.9** hierarchical protocol
against pseudoreplication, **P2.6** agent without synthetic external events).

**E10** answers the document's central question — *with an EQUAL budget, does the
residue beat conventional memory?* Four agents identical in everything but their
signal (6 float64, same EMA, same policy, episodes, seeds and noise):

| condition | result |
|---|---|
| (a) reconstructs **less** content than conventional memory | **yes** — RMSE 0.1018 (residue) vs 0.0827 (content) |
| (b) excess MI with the future > 0 | **yes** — **+0.0165 bits** (noise control ≈ 0) |
| (c) J(residue) > J(content) in both disturbance regimes | **yes** — paired, t ≈ 12 and t ≈ 6 |

**Published caveat:** residue ≈ no-memory (null) — the residue beats
*conventional* memory, not the *absence* of memory. Real telemetry from this
machine (CPU 18.5–60.0 %, RAM ≈ 81 %) is collected into
`resultados/maquina.json` / `resultados/telemetria_real.json` and drives the E10
residue channel in place of the synthetic input, outside the regression because
it is non-deterministic.

## Third external audit — "MUTARIC ev 2" (`docs/10`, in Portuguese)

Same rule, applied this time to **their code**: the attached `e10b.py` was
**executed on this machine** and **58/58 published numbers reproduce exactly**
(difference 0), then ported as **E10b** — seeded, deterministic, regressed by
2 new tests (`E10b_controles`).

E10b asks what happens against **strong** memories of equal 24-bit budget
(magnitude EMA, short window, learned recurrent state), with paired bootstrap
CIs, 200 seeds and an OOD split:

| comparison (Δ = residue − control) | ID | OOD |
|---|---|---|
| vs magnitude EMA | −0.0001272 (unfavorable) | −0.0000237 (unfavorable) |
| vs short window | +0.0000370 (favorable) | −0.0001596 (unfavorable) |
| vs learned recurrent | −0.0001904 (unfavorable) | −0.0003150 (unfavorable) |

**Published verdict (null, with the same prominence as the positive ones):** in
that environment the strong claim *residue > conventional memory of equal
capacity* **does not hold** — the best agent is the learned recurrent state,
and no memory recovers the erased signal (decoder ≈ chance, 0.4985–0.5018).
This is consistent with our own E10 caveat (residue ≈ no-memory) and became a
**written limitation** of our comparator (`docs/09` §7.6) plus two queue
items: **P1.10** (strong controls inside *our* E10 environment) and **P2.7**
(E10c, predictive compressed residue under a non-reconstruction constraint).
The document's first part (`e10.py`, their test files) was **not provided**
and is declared unverifiable.

## Key findings (details in `docs/02_analise_achados.md`)

1. **The relational code does not beat trivial baselines.** `level+delta` reaches
   1.000 on clean data; the relational reader reaches 0.919. Its real advantage is
   **affine invariance** (per-line gain/offset leaves it at 0.919 while the level
   baseline drops to 0.51).
2. **It collapsed under noise** (0.334 = chance at σ=0.10) because edges were hard-
   thresholded at a fixed τ and Hamming decoding has no error correction. **Now
   fixed** by the robust reader (see above): 0.733 at σ=0.10, same split, same τ.
   Remaining failure mode: above σ≈0.30 the reliability weights start to *hurt*
   slightly, because σ̂ itself becomes noisy — reported, not hidden.
3. **Bug found and fixed:** payload decoding under vertex permutation collided on
   isomorphic words (0.146–0.208 measured; 1.000 with one word per isomorphism
   class). There are exactly 11 classes = integer partitions of 6 → theoretical cap
   `log₂(11) = 3.46` bits.
4. **Family-by-polarity is a copied label**, not an emergent reading (always 1.000).
5. **Canonicalising the body *hurts*** (0.919 → 0.666): searching 720 permutations
   multiplies false matches. *(Superseded in E5 by a different device: sorting the
   body rows by a permutation-invariant key instead of searching — see `docs/05`
   §5.3, which also records why the trajectory-prototype search failed at 25%.)*
6. **The "alphabet" is a 1-NN classifier** and the provenance is a scripted
   scenario — the claim must be phrased as pattern recognition, not emergence.
7. **Valence dead zone:** all 25/1800 inconsistencies are joy with `v ≈ −0.075`;
   sadness is always negative. A neutral band is needed.
8. Portability issues on Windows (cp1252 vs `σ`), non-importable package name and
   missing tests — all fixed in this reorganisation.

## Limitations

- **No action yet:** `agente.py` has a real transition and a two-way feedback loop
  (reading changes `S*`, the weights `w` and the threshold τ), but there is no cost,
  no reward and no chosen action; valence still comes from `affect()`, not from a
  dynamics. The agent reads **itself** — no second agent, no contagion, no
  consequence of communication.
- **Landauer here is accounting, not thermodynamics:** the "discarded energy" is a
  dimensionless sum of variances and correlation magnitudes; `k_t` is a constant we
  chose. No Boltzmann constant appears anywhere. Only the *direction* of the
  principle is implemented.
- No memory across glyphs; TEOA's cycles and hysteresis are not modelled here.
- The real `teoa/core.py` is **not** used; `mundo.py` is a scripted stand-in.
- Exploratory: hyper-parameters were chosen by us — including `k_t`, `k_tau`,
  `k_relax`, `β` and `J` — and one metric (reactivity) was redefined *after* seeing
  the data. No pre-registration, no hypothesis test yet.
- Known self-found limitation: `glifo.text_to_digits` drops leading NUL bytes (the
  same limitation found in the MutaCore document; `docs/06` §8.6). Not covered by
  the tests; fixing it would change the digit encoding and numbers already
  published, so it is documented rather than changed blindly.

## Does it feel? ("I don't feel, I compute")

Short answer: **this repository does not claim that it does, and cannot.** What it
adds is an operational fact: previously `X(t+1) = f(X(t))`, so the emotional state
was a *label* travelling beside the trajectory — measured difference exactly
0.00000. Now `X(t+1) = f(X(t), S*(history), w(history), τ(history))` and the
difference is 0.00615, causally produced by what was read and reverted during rest.
That is *operational closure* — a necessary condition for any serious agency claim,
not a sufficient one for feeling. The criterion is symmetric (it would apply to a
human the same way), which is why the remaining gap is the other-minds problem and
not a programming problem. Full argument in `docs/05` §8.

## Next steps

See `docs/04_plano_desenvolvimento.md` (P0–P3, each with acceptance criteria).
**P0.1–P0.5 are done** (isomorphism-aware payload, robust soft decoding,
accuracy-vs-σ curve, clean `run_all.py`, CI on Windows + Linux), and the
MUTARIC ev and ev 2 audits are closed (`docs/09`, `docs/10`); **P1** remains: real
baselines, bootstrap hypothesis tests, perceptual transformations, a neutral band,
**P1.7** (payload as a channel: spreading + decoder — the only MutaCore idea
left as future work), **P1.9** (hierarchical protocol) and **P1.10** (strong
memory controls inside our E10 environment). Then **P2**: wire the
actual TEOA core, a two-agent communication loop, **P2.6** (agent without
synthetic external events) and **P2.7** (E10c, predictive residue with
non-reconstruction). How to resume: `docs/07_continuidade.md`.

## Relation to the TEOA project

Local: `Desktop/Emoções/` (see its `README.md` and `docs/`). The conceptual mapping
between TEOA concepts, this code and the RIC/PIXEL reading model — plus the seven
open gaps — is documented in `docs/03_relacao_pixel_teoa.md`.
