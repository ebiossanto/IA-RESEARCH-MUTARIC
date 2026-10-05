# ricemotions — emoção escrita em pixels

[![CI](https://github.com/ebiossanto/IA-RESEARCH-MUTARIC/actions/workflows/ci.yml/badge.svg)](https://github.com/ebiossanto/IA-RESEARCH-MUTARIC/actions/workflows/ci.yml)

Ponte entre o **projeto TEOA** (Teoria do Estado Ótimo Artificial — *por que* e
*quando* uma emoção surge) e o **projeto PIXEL/RIC** (código de incidência relacional
— *o que* dá para recuperar de um estado escrito em pixels).

Um **episódio** de 6 canais × 32 passos vira **valência + ativação** (TEOA), é
renderizado como um **glifo 48×32** e é lido de volta por um leitor relacional que
tentam recuperar **família afetiva, procedência e uma carga explícita de 5,36 bits**.

> **Status: protótipo exploratório.** Os seis experimentos principais (E1–E6),
> os três de verificação externa (E7–E9, do documento MutaCore), o **E10**
> (paridade de orçamento, da auditoria MUTARIC ev), o **E10b** (controles
> fortes de memória, da auditoria MUTARIC ev 2) e o **E10d** (treinamento
> adversarial + atacante neural, da auditoria MUTARIC ev 3/4) e o **E10e_repl**
> (réplica nossa do protocolo de Pareto, das auditorias MUTARIC ev 5/6) rodam, são
> determinísticos e têm **36 testes** — mas os números do E1–E4 vêm de um mundo
> **roteirizado** (`mundo.py` escreve as procedências à mão) e de um leitor que
> **relê o que foi gravado literalmente**. Leia `docs/02_analise_achados.md` antes de
> citar qualquer número; ele lista o que os resultados **não** sustentam.

---

## Leia nesta ordem

0. `docs/00_indice.md` — índice: o que cada documento responde + ordens de leitura.
1. `docs/01_arquitetura.md` — o que cada módulo faz, formatos, contrato.
2. `docs/02_analise_achados.md` — números + 8 achados (inclui um bug já corrigido).
3. `docs/03_relacao_pixel_teoa.md` — a ponte TEOA × PIXEL: o que está ligado e as 7 lacunas.
4. `docs/04_plano_desenvolvimento.md` — P0–P4 com critério de aceite (P0.1–P0.5 concluídos; P4 = objetivo novo sistema JEV-IA-MUTARIC).
5. `docs/05_residuo_e_agencia.md` — resíduo, Landauer, τ e a **agência de mão dupla**
   (inclui a resposta a *"eu não sinto, eu computo"*).
6. `docs/06_analise_mutacore.md` — análise do documento **MutaCore/RIC**: cada
   afirmação reproduzida numericamente; o que é correto entrou no código, o que não
   é ficou refutado com prova.
7. `docs/07_continuidade.md` — **retomada**: estado atual, regras decididas,
   próximo passo e checklist para adicionar um experimento.
8. `docs/08_historico_completo.md` — **relatório completo**: todos os estudos
   feitos e todas as mudanças de direção.
9. `docs/09_analise_mutaric_ev.md` — auditoria externa **MUTARIC ev**: 5 correções
   adotadas, o **E10** (orçamento igual) e a coleta **real** desta máquina.
10. `docs/10_analise_mutaric_ev2.md` — segunda auditoria **MUTARIC ev 2**:
    o `e10b.py` deles executado aqui (**58/58 números reproduzidos**) e o
    **E10b** — o resíduo **não vence** memórias fortes de igual orçamento.
11. `docs/11_analise_mutaric_ev3_ev4.md` — terceira auditoria **MUTARIC ev 3/4**:
    o `e10d.py` deles executado aqui (**JSON idêntico, 113/113 checagens**) e o
    **E10d** — adversarial reduz vazamento neural, mas **perde** para os controles.
12. `docs/12_analise_mutaric_ev5_ev6.md` — quarta auditoria **MUTARIC ev 5/6**:
    zip **sem código** → **286/286 checagens aritméticas** + a réplica
    **E10e_repl** (200 sementes deles, pareada por semente) aqui.

## Rodar

```bash
pip install -r requirements.txt
python run_all.py --so-testes    # 36 testes de sanidade (segundos)
python run_all.py                # testes + E1-E10 + E10b + E10d + E10e_repl + figuras (~15 min)
python -m ricemotions.experimentos --telemetria   # coleta REAL da máquina (opcional,
                                                  # requer psutil; não regressada)
```

Saídas: `figs/{glifos,grafos_prototipo,robustez,carga,curva_sigma,residuo,agencia,mutacore,e10_orcamento,e10b_controles,e10d_controles,e10e_repl}.png`
e `resultados/resultados.json`; a coleta opcional grava `resultados/maquina.json` e
`resultados/telemetria_real.json` (não determinísticos). No Windows `python` (não `python3`).

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
  experimentos.py           E1-E10, E10b, E10d, E10e_repl, figuras, único lugar com I/O
tests/test_smoke.py         sanidade + regressão dos números publicados (36)
docs/                       13 documentos (índice, arquitetura, análise, ponte, plano, resíduo/agência, MutaCore, continuidade, histórico, auditorias MUTARIC ev, ev 2, ev 3/4 e ev 5/6)
figs/                       figuras geradas
resultados/                 resultados.json (regenerável) + maquina.json e
                            telemetria_real.json (coleta real, não regressada)
```

## Resultados em uma linha

| | limpo | ruído σ=0,10 | brilho | permutação de linhas |
|---|---|---|---|---|
| relacional (RIC) | 0,919 | **0,334** | 0,919 | 0,193 |
| baseline `nivel+delta` | **1,000** | **1,000** | 0,998 | 0,294\*\* |
| carga (5,36 bits) | 1,000 | 1,000 | 1,000 | 0,117 → **1,000**\* |

\* com `codebook_up_to_isomorphism()`; o valor publicado (0,208) era artefato de
colisão entre palavras isomorfas (`docs/02`, A3).
\*\* sob permutação o que foi medido é `delta` puro = 0,294 (e `nível` = 0,254);
`nivel+delta` não roda nessa condição — ver a tabela certa em `docs/02` §1.

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

Também fechado: `codebook_up_to_isomorphism()` no E3 — a carga sob permutação vai de
**0,208 (artefato) para 1,000**.

**2. O resíduo do ambiente tem destino (E5).** O mesmo estado residual, três codificações:

| | classe (leitor cru) | classe (canônico) | resíduo recuperado | linhas gastas |
|---|---|---|---|---|
| espalhado (ruído de pixel, σ=0,11) | **0,270** | 0,270 | **0,000** | 0 (destrutivo) |
| banda dedicada (linhas 16-21) | **0,933** | 0,837 | 0,977 | **6** |
| **simetria (720 permutações)** | 0,303 | **0,837** | **1,000** | **0** |

A simetria só se lê pelo leitor canônico (cru, sem desfazer a permutação, cai para
0,303) — e por esse leitor ela dá **exatamente o mesmo número da banda**. Ou seja:
canonizar custa ~0,10 de acurácia (0,933 → 0,837) e ganha o **teto combinatório**
`log₂720 = 9,49` bits — a *ordenação* dos 6 canais, não as amplitudes (auditoria
MUTARIC ev, correção 2) — sem tocar no orçamento de pixels.

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
Quatro mecanismos novos entraram no código (7 entradas — tabela `docs/06` §2); das
18 afirmações do documento, **6 não passaram** na prova, 4 ficaram parciais ou não
verificáveis e 8 foram confirmadas.

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

## Auditoria externa MUTARIC ev (04/10/2026 — `docs/09`)

Segunda verificação externa, mesma regra: **nada aceito sem reprodução numérica.**
As 5 correções do documento foram adotadas (2 redacionais — "mesma energia" →
"três codificações do mesmo estado residual", `log₂720` como teto combinatório;
2 viraram plano: **P1.9** protocolo hierárquico contra pseudorreplicação e
**P2.6** agente sem evento externo sintético). O E9 agora **declara** o campo não
determinístico (`campos_nao_deterministicos: ["segundos"]`).

O **E10** responde à pergunta central do documento — *com o MESMO orçamento, o
resíduo supera uma memória convencional?* — com quatro agentes idênticos em tudo
exceto o sinal (6 `float64`, mesma EMA, mesma política, mesmos episódios,
sementes e ruído):

| condição | resultado |
|---|---|
| (a) reconstrói **menos** conteúdo que a memória convencional | **sim** — RMSE 0,1018 (AR) vs 0,0827 (AM) |
| (b) MI excedente com o futuro > 0 | **sim** — **+0,0165 bits** (controle de ruído ≈ 0) |
| (c) `J(AR) > J(AM)` nos dois regimes de distúrbio | **sim** — pareado, t ≈ 12 e t ≈ 6 |

**Ressalva publicada:** `AR ≈ A0` (nulo) — o resíduo supera a memória
*convencional*, não a *ausência* de memória. E a coleta **real** desta máquina
(CPU 18,5–60,0%, RAM ~81%) está em `resultados/maquina.json` e
`resultados/telemetria_real.json`, com a carga real alimentando o E10 no lugar do
resíduo sintético — fora da regressão por ser não determinística.

## Auditoria externa MUTARIC ev 2 (04/10/2026 — `docs/10`)

Terceira verificação externa, mesma regra — e desta vez com o **código deles
executado aqui**: o `e10b.py` anexado rodou nesta máquina (**58/58 números
publicados reproduzidos com diferença 0**) e foi portado como **E10b**,
determinístico e regredido (`E10b_controles`, 2 testes novos).

O E10b responde *o que acontece contra memórias **fortes** de igual orçamento
(24 bits)* — EMA de magnitude, janela curta e estado recorrente aprendido,
com IC bootstrap pareado, 200 sementes e teste OOD:

| comparação (Δ = resíduo − controle) | ID | OOD |
|---|---|---|
| vs EMA de magnitude | −0,0001272 (desfavorável) | −0,0000237 (desfavorável) |
| vs janela curta | +0,0000370 (favorável) | −0,0001596 (desfavorável) |
| vs recorrente aprendido | −0,0001904 (desfavorável) | −0,0003150 (desfavorável) |

**Veredito publicado (nulo, com a mesma proeminência dos positivos):** no
ambiente do E10b a formulação forte *resíduo > memória convencional de igual
capacidade* **não se sustenta** — o melhor agente é o recorrente aprendido,
e nenhuma memória recupera o sinal apagado (decodificador ≈ acaso, 0,4985–0,5018).
Isso é coerente com a ressalva `AR ≈ A0` do nosso E10 e virou **limitação
escrita** (`docs/09` §7.6) + duas pendências: **P1.10** (controles fortes no
nosso ambiente do E10) e **P2.7** (E10c, resíduo preditivo com não
reconstrução). A parte 1 do documento (`e10.py`, testes deles) **não foi
fornecida** e fica declarada como não verificável.

## Auditoria externa MUTARIC ev 3/4 (04/10/2026 — `docs/11`)

Quarta verificação externa, mesma regra — o `e10d.py` anexado **rodou aqui**
e regenerou o JSON publicado **idêntico (0 diferenças em 129 números)**;
as tabelas do documento passaram em **113/113 checagens**; o código foi
portado como **E10d** (`E10d_controles`, 2 testes novos). Os experimentos
**E10c** e **E10e** vieram **sem código** e ficam não reproduzíveis por
execução (só checagem aritmética interna).

O E10d responde *o treinamento adversarial reduz a reconstrução neural sem
custo — e vence os controles fortes?* (codificador sigmoidal de 24 bits,
gradiente reverso, λ escolhido só na validação, atacante neural externo,
160 sementes, IC bootstrap):

| resultado | ID | OOD |
|---|---|---|
| ΔJ (com adversário − sem), `IC95%` | **+2,4018×10⁻⁵** [+2,0822×10⁻⁵, +2,7210×10⁻⁵] | **+3,8618×10⁻⁵** [+3,3304×10⁻⁵, +4,4425×10⁻⁵] |
| atacante neural sem → com adversário | 0,55633 → 0,52216 | 0,57977 → 0,55542 |
| vs recorrente E10b (Δ) | **−0,001067** (desfavorável) | **−0,001944** (desfavorável) |

**Vereditos publicados (com a mesma proeminência):** o adversarial **reduz
reconstrução neural sem custo dentro da própria arquitetura** (H3: ICs
estritamente positivos nos dois splits), mas **perde para todos os controles
fortes do E10b** (H4 **refutada**: 8/8 comparações desfavoráveis, ICs
negativos, ~0% de vitórias) e a reconstrução neural segue acima de 50%
mesmo com adversário (H2 só parcial). A seleção de λ foi por **fallback**
(nenhum λ atingiu o limite 0,515 — declarado, não é "restrição satisfeita").

**Ressalva própria, encontrada na nossa verificação:** os ataques
lineares/quadráticos do E10d são **degenerados** — `T = 2*Y−1` com `Y` uint8
vira `{255,1}`, o ridge prevê >99,5% positivo e a "acurácia" ≈ taxa base
(linear == quadrático em 9/9 comparações). Logo, "linear ≈ acaso" ali não
mede reconstrução nenhuma: o que prova o vazamento é o atacante **neural**.
Isso reforça a ressalva do decodificador do `docs/10` §6.4 e virou a
pendência **P1.11** (atacante neural e temporal contra os **nossos**
estados). A versão **linear** da ideia do P2.7 foi implementada de forma
independente pela auditoria (E10c) e deu **nulo** — o P2.7 passa a ser
formulado já com penalidade adversarial.

## Auditorias externas MUTARIC ev 5/6 (04/10/2026 — `docs/12`)

Quinta verificação externa, mesma regra — mas o zip
`MUTARIC_E10e_200_SEMENTES.zip` veio **só com saídas** (JSON, CSV, PNG),
**sem código**. Nada foi aceito assim: (1) **286/286 checagens aritméticas** —
tabelas do ev 5 × JSON × CSV, fórmulas de privacidade, fronteiras de Pareto
recalculadas por não-dominação e **todas** as estatísticas do ev 6 (t de Welch,
gl, ICs, d de Cohen, z de proporções) recalculadas com `scipy`; e (2) uma
**replicação NOSSA do protocolo** — `E10e_repl` (`E10e_repl`, 2 testes novos) —
executada **neste terminal com as mesmas 200 sementes** do ev 5 (70000–70199),
163,6 s, declarada como nossa: testa as alegações, não reproduz os números deles.

| alegação | veredito na réplica (200 sementes, aqui) |
|---|---|
| Pareto ID = {0,3; 1} | **contido** no nosso {0,1; 0,3; 1} |
| Pareto OOD = {0,003} | **não repetido ponto a ponto** — o nosso {0,01} fica na mesma prateleira P = 1 |
| λ = 1 é o melhor score ID e o pior em privacidade | **confirmado** (−0,00362529; P = 0,99138) |
| λ = 1 vaza mais OOD (ev 6, z = 3,7790) | **confirmado** com o pareado por semente: ΔA = +0,00615, IC [0,00460; 0,00767] |
| "utilidade indistinguível" (ev 6, Welch) | o pareado acha diferença pequena mas **fora de zero** (ID +4,38×10⁻⁶; OOD −1,20×10⁻⁵) — publicada dos dois lados |

Os vereditos completos, os desvios do protocolo de 7 pontos deles (λ não fixado
antes do teste, sem ICs, sem atacante temporal — ninguém rodou) e as pendências
reforçadas (**P3.4**, **P1.9**, **P1.11**) estão em `docs/12`.

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

`docs/04_plano_desenvolvimento.md`: **P0 fechado** (testes, codebook de isomorfismo,
leitor soft, curva × σ e CI verde). A fila agora é **P1** — ICs e teste de hipótese
para E1–E4, baseline séria (logística/MLP), transformações perceptivas reais, faixa
de neutro, **P1.7** (carga como canal: espalhamento + decodificador, a única ideia
do MutaCore que ficou como trabalho futuro), **P1.9** (protocolo hierárquico —
correção da auditoria), **P1.10** (controles fortes de memória no ambiente do
E10 — correção da auditoria ev 2) e **P1.11** (atacante neural/temporal contra os
nossos estados — da auditoria ev 3/4). Depois **P2.1**, trocar `mundo.episode()` por
`teoa/core.py` de verdade, **P2.6** (agente sem evento externo sintético) e
**P2.7** (E10c: resíduo preditivo com não reconstrução — já com penalidade
adversarial, após a versão linear dar nulo no E10c externo).

**Objetivo novo (05/10/2026):** o material externo `_MUTARIC Jev.md` propõe o
**sistema JEV-IA-MUTARIC** — o Jev (modelo de decisão estruturada) como camada
probabilística sobre o estado MUTARIC, na divisão *LLM explica · Jev decide ·
MUTARIC regula*, com o experimento **`E11-JEV`** (4 condições, 12 métricas,
H1–H4). Registrado como **P4** em `docs/04` (contrato puro, harness sem Jev,
atacante semântico, calibração ECE/Brier) — **nenhuma alegação sobre o Jev
verificada**: sem acesso ao modelo, e as ressalvas da §9 do documento viraram
regras do projeto.
Como retomar: `docs/07`.

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

**Status: exploratory prototype.** Six experiments (E1–E6), three external
verification runs (E7–E9, from the MutaCore document), **E10** (equal budget,
from the MUTARIC ev audit), **E10b** (strong memory controls, from the
MUTARIC ev 2 audit), **E10d** (adversarial training + neural attacker,
from the MUTARIC ev 3/4 audit) and **E10e_repl** (our own replication of the
Pareto protocol, from the MUTARIC ev 5/6 audits) run deterministically and are covered by **36 tests**,
but the world is **hand-scripted** and the reader **re-reads what the writer
stored literally**. Read `docs/02_analise_achados.md`
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

**New in this cycle (`docs/09`):** the second external audit ("MUTARIC ev") was
verified claim by claim — the only nondeterministic diff really is `E9/segundos`
(now *declared* via `campos_nao_deterministicos`), and the proposition
`F(X,R) ≠ F(X,R')` is protected by the existing tests (0.0 open vs 0.00615
closed). **E10** compares four equal-budget agents (no memory / noise /
conventional content memory / residue; 6 float64, same EMA, policy, episodes,
seeds, noise): **3 of 3 conditions hold** — the residue reconstructs less content
(RMSE 0.1018 vs 0.0827), its excess MI with the future is **+0.0165 bits** (noise
control ≈ 0), and paired J(AR) > J(AM) in both disturbance regimes (t ≈ 12 and
t ≈ 6) — **but AR ≈ A0**: the residue beats conventional memory, not the absence
of memory (a partial null result, published as prominently as the positive ones).
Real telemetry from this machine drives the E10 residue channel in place of the
synthetic input, in non-regressed files.

**New in this cycle (`docs/10`):** the third external audit ("MUTARIC ev 2")
was verified by **execution** — its `e10b.py` was run here and **58/58
published numbers reproduce exactly**; the code was ported as **E10b**
(seeded, deterministic, regressed by 2 new tests). E10b compares the quadratic
residue against *strong* memories of equal 24-bit budget (magnitude EMA, short
window, learned recurrent state) with paired bootstrap CIs, 200 seeds and an
OOD split: **the strong claim is refuted in that environment** — the residue
loses to magnitude EMA (ID −0.0001272, OOD −0.0000237) and to the learned
recurrent model (ID −0.0001904, OOD −0.0003150; all CIs exclude zero), wins
only against the short window in-distribution, and the best agent is the
learned recurrent state; no memory recovers the erased signal above chance.
This null result is published as prominently as the positive ones, written up
as a limitation of our own E10 comparator (`docs/09` §7.6), and turned into
two queue items: **P1.10** (strong controls + OOD + bootstrap CI inside *our*
E10 environment) and **P2.7** (E10c, predictive compressed residue under a
non-reconstruction constraint). The document's first part (`e10.py` and their
test files) was not provided and is declared **unverifiable**.

**New in this cycle (`docs/11`):** the fourth external audit ("MUTARIC ev
3/4") was verified by **execution** — its `e10d.py` was run here and
regenerated the published JSON **identical (0 differences in 129 numbers)**;
the document's tables passed **113/113 checks**; the code was ported as
**E10d** (`E10d_controles`, 2 new tests). **E10c and E10e shipped no code**
and remain unverifiable by execution (internal arithmetic only). E10d shows
that adversarial training **reduces neural reconstruction without cost
inside its own architecture** (ΔJ +2.4018e-5 ID / +3.8618e-5 OOD, both CIs
strictly positive; neural attacker 0.556 → 0.522 and 0.580 → 0.555) **but
loses to every strong E10b control in both splits** (H4 refuted: 8/8
comparisons unfavourable, CIs negative, ≈0 % wins), and neural
reconstruction stays above 50 % even with the adversary (H2 only partial).
λ was chosen by **fallback** — no λ met the 0.515 limit (declared as
fallback, not as a satisfied constraint). **Our own caveat, found during
verification:** the document's linear/quadratic attackers are **degenerate**
(`T = 2Y−1` on uint8 wraps to `{255,1}`, so the ridge predicts >99.5 %
positive and scores ≈ the base rate; linear == quadratic in 9/9 comparisons)
— "linear ≈ chance" there measures nothing, and the neural attacker is the
only real evidence. This reinforces the decoder caveat in `docs/10` §6.4 and
became roadmap item **P1.11** (neural/temporal attackers against *our*
states); the **linear** version of P2.7's idea was independently implemented
by the audit (E10c) and came out **null**, so P2.7 is now specified with an
adversarial penalty.

**New in this cycle (`docs/12`):** the fifth external verification package
("MUTARIC ev 5 / ev 6") shipped **outputs only — no code**, so nothing was
accepted at face value: **286/286 arithmetic checks** (document × JSON × CSV,
privacy formulas, Pareto frontiers recomputed, and every ev 6 statistic — Welch
t/df/p/CI/Cohen's d and the proportion z-tests — recomputed with `scipy`), plus
**our own replication of the protocol executed on this terminal**
(`E10e_repl`, the same 200 seeds 70000–70199, 163.6 s, paired per seed, 2 new
tests). Verdicts: their ID Pareto {0.3; 1} **is contained in ours**
{0.1; 0.3; 1}; **their exact OOD Pareto did not repeat** (ours {0.01} vs theirs
{0.003} — same P = 1 plateau, different point, published with the same
prominence); λ = 1's best ID score and worst privacy in all four corners were
**confirmed**, and its larger OOD leakage was confirmed with the **paired
per-seed bootstrap ev 6 could not run** (it saved no per-seed data):
ΔA = +0.00615 [0.00460, 0.00767]. The paired test also finds tiny but nonzero
utility differences (ID +4.38e-6, OOD −1.20e-5), so ev 6's "no detectable
utility difference" is published as **test-dependent**. Adopted: save per-seed
scores *and* per-seed attacker accuracies, prefer paired over Welch at this
sample size, and fix λ before touching the test set (**P3.4**, reinforced by
their own lost OOD frontier).

Full English documentation: [`README.en.md`](README.en.md). Architecture, findings,
TEOA↔PIXEL mapping and roadmap in `docs/` (Portuguese).
