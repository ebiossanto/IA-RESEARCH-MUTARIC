# ricemotions — emoção escrita em pixels

Ponte entre o **projeto TEOA** (Teoria do Estado Ótimo Artificial — *por que* e
*quando* uma emoção surge) e o **projeto PIXEL/RIC** (código de incidência relacional
— *o que* dá para recuperar de um estado escrito em pixels).

Um **episódio** de 6 canais × 32 passos vira **valência + ativação** (TEOA), é
renderizado como um **glifo 48×32** e é lido de volta por um leitor relacional que
tentam recuperar **família afetiva, procedência e uma carga explícita de 5,36 bits**.

> **Status: protótipo exploratório.** Os quatro experimentos (E1–E4) rodam, são
> determinísticos e têm testes — mas os números são de um mundo **roteirizado**
> (`mundo.py` escreve as procedências à mão) e de um leitor que **relê o que foi
> gravado literalmente**. Leia `docs/02_analise_achados.md` antes de citar qualquer
> número; ele lista o que os resultados **não** sustentam.

---

## Leia nesta ordem

1. `docs/01_arquitetura.md` — o que cada módulo faz, formatos, contrato.
2. `docs/02_analise_achados.md` — números + 8 achados (inclui um bug já corrigido).
3. `docs/03_relacao_pixel_teoa.md` — a ponte TEOA × PIXEL: o que está ligado e as 7 lacunas.
4. `docs/04_plano_desenvolvimento.md` — P0–P3 com critério de aceite.

## Rodar

```bash
pip install -r requirements.txt
python run_all.py --so-testes    # 14 testes de sanidade (segundos)
python run_all.py                # testes + E1-E4 + figuras (alguns minutos)
```

Saídas: `figs/{glifos,grafos_prototipo,robustez,carga}.png` e
`resultados/resultados.json`. No Windows `python` (não `python3`).

## Estrutura

```
README.md  README.en.md     documentação (PT / English)
requirements.txt .gitignore run_all.py
ricemotions/                pacote importável
  mundo.py                  TEOA: episódios, valência, rótulos (sem I/O)
  glifo.py                  PIXEL/RIC: escrever, ler, grafos, alfabetos (sem I/O)
  experimentos.py           E1-E4, figuras, único lugar com I/O
tests/test_smoke.py         sanidade + regressão dos números publicados
docs/                       4 documentos (arquitetura, análise, ponte, plano)
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

## Três limites que não se deve esquecer

1. **Roteiro, não emergência** — as procedências são cenários escritos à mão
   (`mundo.py`, aviso no próprio arquivo). O que se testa é o *código*, não a
   emergência da emoção a partir de um agente.
2. **Sem agente, sem feedback** — ninguém *escolhe* nada e quem lê um glifo não
   muda (`docs/03`, L2/L3).
3. **Exploratório** — τ, `d_min`, janelas e limiares foram escolhidos por nós.
   Não há pré-registro nem teste de hipótese. Ver `docs/04`, P1.

## Próximo passo

`docs/04_plano_desenvolvimento.md`, **P0**: corrigir a carga sob permutação (P0.2),
tornar o grafo robusto a ruído (P0.3) e publicar a curva acurácia × σ (P0.4).

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

**Status: exploratory prototype.** Four experiments (E1–E4) run deterministically and
are covered by tests, but the world is **hand-scripted** and the reader **re-reads
what the writer stored literally**. Read `docs/02_analise_achados.md` before quoting
any number: it lists what the results do **not** support.

| | clean | noise σ=0.10 | brightness | row permutation |
|---|---|---|---|---|
| relational (RIC) | 0.919 | **0.334** | 0.919 | 0.193 |
| `nivel+delta` baseline | **1.000** | **1.000** | 0.998 | 0.294 |
| payload (5.36 bits) | 1.000 | 1.000 | 1.000 | 0.117 → **1.000**\* |

\* using `codebook_up_to_isomorphism()`; the published 0.208 was an artifact of
isomorphic-word collisions.

**Honest reading:** the relational code wins on **affine invariance** and loses on
**noise** and on **raw accuracy** — a trivial baseline reaches 1.000 on clean data.

Full English documentation: [`README.en.md`](README.en.md). Architecture, findings,
TEOA↔PIXEL mapping and roadmap in `docs/` (Portuguese).
