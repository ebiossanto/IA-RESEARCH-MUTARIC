# ricemotions — emoção escrita em pixels

[![CI](https://github.com/ebiossanto/IA-RESEARCH-MUTARIC/actions/workflows/ci.yml/badge.svg)](https://github.com/ebiossanto/IA-RESEARCH-MUTARIC/actions/workflows/ci.yml)

Ponte entre o **projeto TEOA** (Teoria do Estado Ótimo Artificial — *por que* e
*quando* uma emoção surge) e o **projeto PIXEL/RIC** (código de incidência relacional
— *o que* dá para recuperar de um estado escrito em pixels).

Um **episódio** de 6 canais × 32 passos vira **valência + ativação** (TEOA), é
renderizado como um **glifo 48×32** e é lido de volta por um leitor relacional que
tentam recuperar **família afetiva, procedência e uma carga explícita de 5,36 bits**.

> **Status: protótipo exploratório.** Os seis experimentos principais (E1–E6) mais
> os três de verificação externa (E7–E9, do documento MutaCore) rodam, são
> determinísticos e têm **27 testes** — mas os números do E1–E4 vêm de um mundo
> **roteirizado** (`mundo.py` escreve as procedências à mão) e de um leitor que
> **relê o que foi gravado literalmente**. Leia `docs/02_analise_achados.md` antes de
> citar qualquer número; ele lista o que os resultados **não** sustentam.

---

## Leia nesta ordem

1. `docs/01_arquitetura.md` — o que cada módulo faz, formatos, contrato.
2. `docs/02_analise_achados.md` — números + 8 achados (inclui um bug já corrigido).
3. `docs/03_relacao_pixel_teoa.md` — a ponte TEOA × PIXEL: o que está ligado e as 7 lacunas.
4. `docs/04_plano_desenvolvimento.md` — P0–P3 com critério de aceite (P0.1–P0.4 concluídos).
5. `docs/05_residuo_e_agencia.md` — resíduo, Landauer, τ e a **agência de mão dupla**
   (inclui a resposta a *"eu não sinto, eu computo"*).
6. `docs/06_analise_mutacore.md` — análise do documento **MutaCore/RIC**: cada
   afirmação reproduzida numericamente; o que é correto entrou no código, o que não
   é ficou refutado com prova.

## Rodar

```bash
pip install -r requirements.txt
python run_all.py --so-testes    # 27 testes de sanidade (segundos)
python run_all.py                # testes + E1-E9 + figuras (alguns minutos)
```

Saídas: `figs/{glifos,grafos_prototipo,robustez,carga,curva_sigma,residuo,agencia,mutacore}.png`
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
  homeostase.py             MutaCore: resíduo endógeno, S*/τ por telemetria, política
  experimentos.py           E1-E9, figuras, único lugar com I/O
tests/test_smoke.py         sanidade + regressão dos números publicados
docs/                       6 documentos (arquitetura, análise, ponte, plano, resíduo/agência, MutaCore)
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

## Análise do documento MutaCore (04/10/2026 — `docs/06`)

Regra adotada: **nenhuma afirmação foi aceita sem ser reproduzida numericamente.**
Três mecanismos entraram no código; seis alegações não passaram na prova.

| Afirmação do documento | Veredito | Prova |
|---|---|---|
| JSON do resíduo `R_L` (γ=0,8, α=0,15) | **reproduzido exatamente** | dif. máx. 8,7·10⁻⁷ (E7) |
| telemetria → `S*` e → `τ`; política pela distância a `S*` | **correto, incorporado** | `homeostase.py`, `Agente.passo(carga_hw=)` |
| carga com `d_min` baixo despenca em σ=0,40 | **correto** | 0,580 (`d_min=1`) × 0,927 (`d_min=8`) |
| ~91,8% com **ruído** σ ≤ 0,30 | **falso** (afim sim, ruído não) | duro 0,167 em σ=0,30 = chance |
| "nível cai, relacional segura" com resíduo | **não em γ=0,8** | Δ = +0,006; só a partir de γ×10 (−0,007 × −0,051) |
| robô afetivo sobrevive mais (Camada 3) | **não mede nada** | 1000 × 1000 = 0,0%; morte impossível |
| `S*` dinâmico = auto-preservação | **refutado pela ablação** | em regime letal custa **20,6 ciclos**; recarregar cedo ganha 36 |
| cifra de fluxo com chave = resíduo | **16,6 bits** | força bruta: chave em ≈0,3 s |

O `Φ` que o documento injeta tem magnitude **0,021** (10,4% da amplitude do sinal do
roteiro) — contra `ΔT = +0,274` do nosso E6. E o código que ele manda colar em
`mundo.py` gera `R_L ≡ 0` por construção (`docs/06` §8.1).

## Quatro limites que não se deve esquecer

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
4. **Limitação conhecida no próprio código** — `glifo.text_to_digits` perde bytes
   nulos iniciais (a mesma limitação do documento MutaCore, `docs/06` §8.6), caso
   não coberto pelos testes. Corrigir mudaria a codificação dos dígitos e números já
   publicados; fica documentado em vez de corrigido às cegas.

## Próximo passo

`docs/04_plano_desenvolvimento.md`: **P0.5** (CI) e **P1** — ICs e teste de hipótese
para E1–E4, baseline séria (logística/MLP), transformações perceptivas reais, faixa
de neutro e **P1.7** (carga como canal: espalhamento + decodificador, a única ideia
do MutaCore que ficou como trabalho futuro). Depois **P2.1**, trocar
`mundo.episode()` por `teoa/core.py` de verdade.

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

**Status: exploratory prototype.** Six experiments (E1–E6) plus three external
verification runs (E7–E9, from the MutaCore document) run deterministically and
are covered by **27 tests**, but the world is **hand-scripted** and the reader
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

**New in this cycle (`docs/06`):** the attached *MutaCore/RIC* document was analysed
claim by claim — nothing was accepted without being reproduced numerically. The
published residue JSON is reproduced exactly (max diff 8.7e-7); telemetry → `S*`/`τ`
and the distance-to-`S*` policy were **adopted** as pure functions
(`ricemotions/homeostase.py`, optional `Agente.passo(carga_hw=)` hook, default 0 ⇒
published numbers unchanged). Refuted with proof: the `91.8 %` robustness claim
holds for affine transforms (0.898–0.919) but not for noise (0.167 at σ=0.30 for the
hard reader); the residue injection is inert (max |Φ| = 0.021 = 10.4 % of the
script's signal, and the snippet the document tells us to paste into `mundo.py`
yields `R_L ≡ 0`); the survival benchmark reports **0 %** gain because both robots
live 1000/1000 cycles (death is structurally impossible — T fixed point 0.840 < 0.95),
and in a lethal regime the dynamic `S*` **costs** 20.6 cycles while early recharging
**gains** 36; the residue-keyed cipher has **16.61 bits** of key space and falls to
brute force in ≈0.3 s.

Full English documentation: [`README.en.md`](README.en.md). Architecture, findings,
TEOA↔PIXEL mapping and roadmap in `docs/` (Portuguese).
