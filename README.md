# ricemotions — emoção escrita em pixels

Ponte entre o **projeto TEOA** (Teoria do Estado Ótimo Artificial — *por que* e
*quando* uma emoção surge) e o **projeto PIXEL/RIC** (código de incidência relacional
— *o que* dá para recuperar de um estado escrito em pixels).

Um **episódio** de 6 canais × 32 passos vira **valência + ativação** (TEOA), é
renderizado como um **glifo 48×32** e é lido de volta por um leitor relacional que
tentam recuperar **família afetiva, procedência e uma carga explícita de 5,36 bits**.

> **Status: protótipo exploratório.** Os quatro experimentos (E1–E4) mais os dois
> novos (E5 resíduo, E6 agência) rodam, são determinísticos e têm **21 testes** — mas
> os números do E1–E4 vêm de um mundo **roteirizado** (`mundo.py` escreve as
> procedências à mão) e de um leitor que **relê o que foi gravado literalmente**.
> Leia `docs/02_analise_achados.md` antes de citar qualquer número; ele lista o que
> os resultados **não** sustentam.

---

## Leia nesta ordem

1. `docs/01_arquitetura.md` — o que cada módulo faz, formatos, contrato.
2. `docs/02_analise_achados.md` — números + 8 achados (inclui um bug já corrigido).
3. `docs/03_relacao_pixel_teoa.md` — a ponte TEOA × PIXEL: o que está ligado e as 7 lacunas.
4. `docs/04_plano_desenvolvimento.md` — P0–P3 com critério de aceite (P0.1–P0.4 concluídos).
5. `docs/05_residuo_e_agencia.md` — resíduo, Landauer, τ e a **agência de mão dupla**
   (inclui a resposta a *"eu não sinto, eu computo"*).

## Rodar

```bash
pip install -r requirements.txt
python run_all.py --so-testes    # 21 testes de sanidade (segundos)
python run_all.py                # testes + E1-E6 + figuras (alguns minutos)
```

Saídas: `figs/{glifos,grafos_prototipo,robustez,carga,curva_sigma,residuo,agencia}.png`
e `resultados/resultados.json`. No Windows `python` (não `python3`).

## Estrutura

```
README.md  README.en.md     documentação (PT / English)
requirements.txt .gitignore run_all.py
ricemotions/                pacote importável
  mundo.py                  TEOA: episódios, valência, rótulos (sem I/O)
  glifo.py                  PIXEL/RIC: escrever, ler, grafos, alfabetos (sem I/O)
  residuo.py                E5: geração, roteamento (banda/simetria), Landauer, τ
  agente.py                 E6: transição + mão dupla (S*, w, τ realimentados)
  experimentos.py           E1-E6, figuras, único lugar com I/O
tests/test_smoke.py         sanidade + regressão dos números publicados
docs/                       5 documentos (arquitetura, análise, ponte, plano, resíduo/agência)
figs/                       figuras geradas
resultados/                 resultados.json (regenerável)
```

## Resultados em uma linha

| | limpo | ruído σ=0,10 | brilho | permutação de linhas |
|---|---|---|---|---|
| relacional (RIC) | 0,919 | **0,334** | 0,919 | 0,193 |
| baseline `nivel+delta` | **1,000** | **1,000** | 0,998 | 0,294 |
| carga (5,36 bits) | 1,000 | 1,000 | 1,000 | 0,117 → **1,000**\* |

\* com `codebook_up_to_isomorfismo()`; o valor publicado (0,208) era artefato de
colisão entre palavras isomorfas (`docs/02`, A3).

**Leitura correta:** o código relacional ganha em **invariância afim** (brilho e
descalibração derrubam a baseline de nível para 0,51) e perde em **ruído** e em
**acurácia pura**. Não há, hoje, evidência de que a leitura relacional seja
*necessária* — a baseline trivial faz 1,000 no teste limpo.

## Resultados novos (04/10/2026 — `docs/05`)

**1. O colapso sob ruído era do limiar, não do código.** O leitor novo estima `σ̂`
pela redundância R=3 do próprio glifo, corrige a atenuação e **ignora** par cujo
sinal é menor que o ruído (em vez de virar bit sorteado):

| σ | leitor duro (τ fixo) | **leitor robusto** |
|---|---|---|
| 0,00 | **0,919** | 0,892 |
| 0,10 | 0,338 | **0,733** |
| 0,20 | 0,174 | **0,544** |
| 0,40 | 0,167 (=chance) | 0,308 |

Também fechado: `codebook_up_to_isomorfismo()` no E3 — a carga sob permutação vai de
**0,208 (artefato) para 1,000**.

**2. O resíduo do ambiente tem destino (E5).** Mesma energia, três roteamentos:

| | classe (leitor cru) | classe (canônico) | resíduo recuperado | linhas gastas |
|---|---|---|---|---|
| espalhado (ruído de pixel, σ=0,11) | **0,270** | 0,270 | **0,000** | 0 (destrutivo) |
| banda dedicada (linhas 16-21) | **0,933** | 0,837 | 0,977 | **6** |
| **simetria (720 permutações)** | 0,303 | **0,837** | **1,000** | **0** |

A simetria só se lê pelo leitor canônico (cru, sem desfazer a permutação, cai para
0,303) — e por esse leitor ela dá **exatamente o mesmo número da banda**. Ou seja:
canonizar custa ~0,10 de acurácia (0,933 → 0,837) e ganha `log₂720 = 9,49` bits de
resíduo sem tocar no orçamento de pixels.

**3. Agência de mão dupla (E6).** O estado lido altera as **próprias regras**:

| | aberto (antes) | fechado (agora) |
|---|---|---|
| mesma transição com resíduo alto vs nulo | **0,00000** | **0,00615** |
| tensão `X[T]` sob Landauer | 0,248 | **0,522** |
| τ médio (resíduo → limiar) | 0,700 | **0,828** |
| desvio de `S*` → após repouso | — | +0,250 → **+0,020** (temporário) |

Com τ exausto (0,90) o sistema ganha **60% menos relações novas** sob estímulo fraco
(0,067 → 0,027): "mau humor" operacional = incapacidade de incorporar informação.

## Três limites que não se deve esquecer

1. **Roteiro, não emergência** — as procedências são cenários escritos à mão
   (`mundo.py`, aviso no próprio arquivo). O que se testa é o *código*, não a
   emergência da emoção a partir de um agente. **Lacuna L1 aberta.**
2. **Feedback de si, não de outrem** — o `Agente` lê a si mesmo e muda as próprias
   regras (`docs/05` §6), mas ninguém lê ninguém: não há contágio nem consequência
   da comunicação, e a valência ainda sai de `affect()`. **L2/L3 parciais.**
3. **Exploratório** — τ, `d_min`, janelas, limiares e os ganhos `k_t`, `k_tau`,
   `k_relax`, `β`, `J` foram escolhidos por nós, alguns *depois* de ver o dado
   (lista em `docs/05` §7). Não há pré-registro, IC nem teste de hipótese.
   Ver `docs/04`, P1.

## Próximo passo

`docs/04_plano_desenvolvimento.md`: **P0.5** (CI) e **P1** — ICs e teste de hipótese
para E1–E4, baseline séria (logística/MLP), transformações perceptivas reais, faixa
de neutro. Depois **P2.1**, trocar `mundo.episode()` por `teoa/core.py` de verdade.

---

## English summary

**ricemotions** is the bridge between the **TEOA** project (Target/Artificial Optimal
State Theory — *why* and *when* an emotion arises) and the **PIXEL/RIC** project
(a relational-incidence code read from *pixels* — *what* can be recovered from a
state written as an image).

A 6-channel × 32-step episode becomes **valence + activation**, is rendered as a
48×32 **glyph** with four bands (level / polarity / body / payload), and is read back
by a relational reader that decodes **affective family, provenance and an explicit
5.36-bit payload**.

**Status: exploratory prototype.** Six experiments (E1–E6) run deterministically and
are covered by **21 tests**, but the world is **hand-scripted** and the reader
**re-reads what the writer stored literally**. Read `docs/02_analise_achados.md`
before quoting any number: it lists what the results do **not** support.

| | clean | noise σ=0.10 | brightness | row permutation |
|---|---|---|---|---|
| relational (RIC), hard threshold | 0.919 | **0.334** | 0.919 | 0.193 |
| `nivel+delta` baseline | **1.000** | **1.000** | 0.998 | 0.294 |
| payload (5.36 bits) | 1.000 | 1.000 | 1.000 | 0.117 → **1.000**\* |
| **robust reader** (σ̂ from R=3 redundancy, attenuation correction, reliability weights) | 0.892 | **0.733** | — | — |

\* using `codebook_up_to_isomorphism()`; the published 0.208 was an artifact of
isomorphic-word collisions.

**Honest reading:** the relational code wins on **affine invariance** and loses on
**noise** and on **raw accuracy** — a trivial baseline reaches 1.000 on clean data.
The collapse under noise was a property of the **threshold**, not of the relational
code (0.334 → 0.733 at σ=0.10).

**New in this cycle (`docs/05`):** environment residue routed three ways (spread →
0.270 accuracy / 0.000 residue recovered; band → 0.933 raw / 0.977 / 6 rows;
**720 symmetries of the canonical body → 0.837 under the canonical reader — the
same as the band — / 1.000 / 0 rows**), a Landauer-style feedback filter (tension
0.248 → 0.522, target temporarily shifted and relaxed back), residue-driven τ (60%
fewer *new* relations under a weak stimulus when exhausted), and an
**operational agency criterion**: same state + different residue history →
transition differs by **0.00615** when closed vs exactly **0.00000** when open.

Full English documentation: [`README.en.md`](README.en.md). Architecture, findings,
TEOA↔PIXEL mapping and roadmap in `docs/` (Portuguese).
