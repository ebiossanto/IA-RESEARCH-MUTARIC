# 08 — Histórico completo: direções, decisões e estudos

> **Relatório do trabalho** — de onde veio, o que foi estudado, o que mudou de
> direção e onde isso parou. Companheiro de `docs/07_continuidade.md` (frente) e
> `docs/00_indice.md` (mapa). Todos os números vêm de `resultados/resultados.json`
> e estão marcados com a chave correspondente.

---

## 1. Objeto do trabalho

Duas perguntas de dois projetos diferentes, costuradas por este repositório:

| polo | pergunta | onde vive |
|---|---|---|
| **TEOA** — Teoria do Estado Ótimo Artificial | *quando* e *por que* uma emoção surge e persiste (estado diante de um alvo `s*`) | `Desktop/Emoções/` (`teoa/core.py`) |
| **PIXEL/RIC** — código de incidência relacional | *o que* dá para recuperar de um estado escrito em **pixels** (informação nas relações entre linhas) | repositório PIXEL — **não localizado** (`docs/03` §5) |

`ricemotions` é o terceiro elemento: recebe o estado, escreve-o como **glifo
48×32**, e tenta lê-lo de volta com o RIC — 4 faixas (nível, polaridade, corpo,
carga), 6 classes de procedência, 3 famílias e **5,36 bits** de carga explícita
(`carga.bits`, `d_min=4` → 41 palavras).

**Uma frase:** um episódio (6 canais × 32 passos) vira valência + ativação, vira
imagem, e a imagem é relida por um código que decodifica família, procedência e
carga — com a pergunta constante: *isso é leitura relacional ou reconhecimento de
um roteiro?* (`docs/02` A6).

## 2. Cronologia — seis ciclos em um dia (04/10/2026)

| ciclo | commit | o que mudou |
|---|---|---|
| **0** (pré-repositório) | — | pasta `files ricemotions` com **espaço no nome** (impedia `python -m`), imports relativos que quebram, `../figs` implícito, **zero testes**, E1–E4 soltos |
| **1** | `389272a` | reorganização: pacote `ricemotions/` importável, imports absolutos, `RAIZ/figs`, **21 testes**, `README`/`README.en`, `docs/01`–`docs/04`; números **não alterados** |
| **2** | `fdf6203` | **E5 resíduo, E6 agência, leitor robusto** (`docs/05`); fecha P0.1–P0.4; incorpora os 3 pedidos do usuário (Landauer, τ, isomorfismo); testes 21 |
| **3** | `8800c9f` | **ciclo MutaCore**: análise do anexo `MUTACORE _ RIC.md` com provas (`docs/06`), `homeostase.py`, E7–E9, testes 21 → **27**, `figs/mutacore.png` |
| **4** | `d88ef3f` | **GitHub + CI**: repositório `ebiossanto/IA-RESEARCH-MUTARIC` (privado na época; **tornado público** em 04/10/2026), `.github/workflows/ci.yml` (Windows + Linux, 27/27), badge, revisão de consistência (P0.5 fecha) |
| **5** (atual) | — | **organização final**: `docs/00` (índice), `docs/07` (continuidade), `docs/08` (este), auditoria de consistência entre documentos, chave `tau_medio_landauer_off` no JSON |

Linha do tempo interna (ciclos 1–3): as datas e o "antes/depois" de cada correção
estão em `docs/01` §7, com a nota de cronologia sobre as correções do E5/E6.

## 3. Os estudos realizados

### 3.1 Inventário

| # | pergunta | método (1 linha) | achado-chave (chave do JSON) |
|---|---|---|---|
| **E1** | a procedência se lê nas RELAÇÕES? | 1-NN sobre o grafo do corpo × LDA sobre `nível/delta/nivel+delta`, 2400/900/1800 | limpo **0,919** × baseline **1,000**; sob ruído σ=0,10 **0,334** (acaso); sob brilho o `nível` cai a **0,509** e o relacional fica (**`transformacoes`**) |
| **E2** | família por nível ou por polaridade? | `read_family_level` × `read_family_relational` | `fam_nivel` **0,986** × `fam_polaridade` **1,000** sempre ⇒ rótulo embutido, canário de sanidade |
| **E3** | capacidade × robustez da carga? | codebooks `d_min∈{1..8}` × σ × permutação (720) | `d_min=1` **7,67 bits** → **0,580** em σ=0,40; `d_min=8` **2,58 bits** → **0,927**; permutação 0,117 → 0,208 (artefato) → **1,000** com `codebook_up_to_isomorphism` |
| **E4** | pipeline completo × baselines? | família mascarada na decodificação | `pipeline_completo` **0,986** limpo / 0,843 σ=0,10 — abaixo do 1,000 da baseline |
| **curva σ** | quanto o limiar fixo colapsa? | 4 leitores × 7 valores de σ, mesma divisão | duro **0,338 → 0,733** (σ=0,10); 0,194 → 0,646 (0,15); **0,167 → 0,308** (0,40); limpo 0,919 → **0,892** (**`curva_sigma`**) |
| **E5** | a mesma energia de resíduo, três destinos? | espalhado × banda × simetria (720 permutações), 300 glifos | A: classe **0,270**, resíduo **0,000**, 0 linhas · B: **0,933/0,837**, resíduo **0,977**, 6 linhas · C: **0,303/0,837**, resíduo **1,000**, **0 linhas**; custo da canonicização **0,933→0,837** (**`E5_residuo`**) |
| **E6** | a leitura realimenta as PRÓPRIAS regras? | 3 agentes (aberto × Landauer × sem Landauer) + critério de mão dupla | critério **0,00000** aberto × **0,00615** fechado; tensão **0,248→0,522**; τ **0,700→0,828**; `S*` desvio **+0,250→+0,020**; exaustão: ganhos **0,067→0,027 (−60%)** (**`E6_agencia`**) |
| **E7** | o resíduo MutaCore reproduz o JSON? e a previsão vale? | reprodução + dose-resposta γ=0,8/×10/×100 com controle | dif. máx. **8,7·10⁻⁷**; \|Φ\|máx **0,021 = 10,4%** do sinal; γ=0,8 Δ=**+0,006** (nulo); γ×10 **−0,051** nível × **−0,007** relacional; carga **0,000** (**`E7_residuo_mutacore`**) |
| **E8** | o benchmark mede emoção? | reprodução fiel + ablação 2×2×2 + varredura + regime letal | 1000×1000 = **0%**; morte impossível (T fixo **0,840 < 0,95**, `E` mín **0,185**); letal: **47,4 ± 5,4** (S\* din) × **68,0** (S\* fixo) × 32,0 ⇒ S\* dinâmico **−20,6 ciclos**, recarregar cedo **+36** (**`E8_sobrevivencia`**) |
| **E9** | a cifra com chave = resíduo tem quantos bits? | varredura de `R_L ∈ [0,1)` passo 10⁻⁵ + força bruta | **100001 chaves = 16,61 bits**; chave `0,03452` recuperada em **≈0,3 s** (3453 candidatos) (**`E9_chave_residuo`**) |

Fora dos "E": `varredura_tau_validacao` (τ=**0,7** escolhido **na validação**, 0,9256
com 139 grafos) e `demo_mensagem` ("Ganhei!", 11 glifos, 11/11 símbolos até σ=0,30).

### 3.2 O que cada ciclo produziu

- **Ciclo 1 (E1–E4):** o resultado que rege todo o resto — **o código relacional
  não vence as baselines triviais** (`docs/02` A1); a contribuição demonstrada é a
  **invariância afim**, não a acurácia. Daí saem 8 achados (A1–A8) e a lista de
  limitações que virou plano.
- **Ciclo 2 (`docs/05`):** três entregas conceituais + três mecânicas: filtro de
  Landauer (energia apagada → tensão), τ como humor (resíduo → reatividade),
  resíduo como simetria (E5) e agência de mão dupla (E6). Fecha P0.1–P0.4
  (codebook de isomorfismo, leitor soft, curva × σ).
- **Ciclo 3 (`docs/06`):** verificação externa — 18 afirmações, 8 confirmadas,
  **6 refutadas**, 4 parciais/não verificáveis; 4 mecanismos novos no código
  (7 entradas, `docs/06` §2) e 6 recusas documentadas (§9).
- **Ciclo 4:** publicação — repositório (privado, hoje **público**), CI verde nas duas plataformas,
  badge e revisão de consistência (fecha P0.5).
- **Ciclo 5:** organização — índice, continuidade, este relatório, auditoria
  (tabela abaixo) e a chave de JSON que faltava.

## 4. Mudanças de direção

### 4.1 Recusas externas (com prova registrada)

| direção proposta | por que não foi seguida | onde |
|---|---|---|
| repositório **PIXEL** como referência | pasta vazia e nenhum repo "pixel" na conta — **não localizado**; 4 correspondências ficam em aberto | `docs/03` §5, lacuna L7 |
| **cifra por resíduo** do MutaCore (§F) | chave de **16,6 bits**: força bruta em ≈0,3 s; incorporar daria *impressão* de canal seguro inexistente | `docs/06` §5, §9 |
| **benchmark de sobrevivência** como "Camada 3" (§E) | métrica **constante** nos parâmetros publicados (0% de ganho, morte impossível); em regime letal mede a **política de recarga**, não a emoção — E6 continua sendo o experimento de agência válido | `docs/06` §4, §9 |
| **telemetria `psutil` ligada por padrão** | I/O e não-determinismo no núcleo quebrariam a reprodutibilidade; fica `homeostase.telemetria()` opcional, nunca usada em teste | `docs/06` §9, `docs/01` §6 |
| **espalhamento por Walsh** (§F) | sem decodificador não há o que testar (`landauer_stress` nunca é usado lá) → vira **item futuro P1.7** | `docs/06` §8.5/§9 |
| **reescrever `mundo.episode`** com o loop de Φ | alteraria os conjuntos e **todos** os números publicados; o resíduo do MutaCore vive em `homeostase`, fora do caminho dos dados | `docs/06` §9 |

### 4.2 Refutações internas (o trabalho consigo mesmo)

Os achados que **pioraram a própria história** e por isso estão publicados:

1. **A1 — a hipótese relacional não vence a baseline.** `nivel+delta` = 1,000 no
   limpo; o relacional = 0,919. A frase a defender passa a ser "invariância afim",
   não "acurácia". (`docs/02` A1)
2. **A2 — o colapso sob ruído era do limiar**, não do código: leitor duro 0,334 em
   σ=0,10; corrigido com de-atenuação + pesos (**0,733**). Ficou aberto só o item
   (b), τ com zona morta → agora **P1.8** no plano. (`docs/02` A2)
3. **A3 — bug de colisão de isomorfismos:** o 0,208 publicado era **artefato**;
   com uma palavra por classe de isomorfismo, **1,000**. (`docs/02` A3, `docs/05` §5.4)
4. **A4 — `fam_polaridade` = 1,000 é rótulo copiado**, rebaixado a canário de
   sanidade. (`docs/02` A4)
5. **A5 — "canonicalizar o grafo" não foi feito** (só ordenação por chave
   invariente); o custo medido **0,933 → 0,837**; a ação original continua aberta
   (P1.5). (`docs/02` A5, `docs/05` §5)
6. **A6 — o "alfabeto" é 1-NN e a procedência é roteiro**: "nada emerge de um
   agente". (`docs/02` A6)
7. **A7 — zona morta da valência**: 25/1800 erros perto de `v≈0` ⇒ faixa de neutro
   (P1.4). (`docs/02` A7)

### 4.3 Redefinições no meio do caminho

- **Métrica de reatividade reescrita depois de ver o dado** (probabilidade total →
  ganhos e perdas separados). Registrada como escolha pós-hoc; a lista completa de
  graus de liberdade é **P1.6** e ainda está incompleta. (`docs/05` §7.5)
- **Primeira versão do E5 falhou:** identificar a permutação por protótipos de
  trajetória acertou **25%**; substituída pela **forma canônica**. (`docs/05` §5.3)
- **Bug de amostragem do E5** (`Ite[:300]` = só classe 0): números de B corrigidos
  de 0,983 → **0,933** — com aviso a quem reproduzir commits anteriores. (`docs/05` §7.6)
- **Dois conjuntos γ/α/λ incompatíveis** no documento MutaCore: só o segundo gera o
  JSON publicado; adotado o que reproduz. (`docs/06` §8.2)
- **τ médio "Landauer off"**: número citado em `docs/05` sem chave no JSON —
  corrigido neste ciclo com `tau_medio_landauer_off` (**0,805**).
- **Mundo permanece roteirizado** — decisão de escopo **mantida e declarada**
  (aviso no `mundo.py`, limite 1 do README), em vez de disfarçada de emergência.

### 4.4 Pedidos do usuário incorporados

| pedido | resultado |
|---|---|
| "pegue a energia lógica descartada e injete em T/C" (filtro de Landauer) | `residuo.energia_descartada` + `agente.modular(landauer=True)`; E6 mostra tensão 0,248 → 0,522 |
| "τ sobe com resíduo ambiente = mau humor/exaustão" | `residuo.tau_efetivo`, τ limitado a [0,45; 0,95]; exaustão medida em E6 (−60% de ganhos) |
| isomorfismo de resíduo (720 permutações) | E5 — rota simetria recupera **1,000** do resíduo com **0 linhas** |
| "dois agentes no mesmo estado produzem transições diferentes?" | `criterio_mao_dupla`: **0,00615** fechado × **0,00000** aberto |
| resposta a *"eu não sinto, eu computo"* | `docs/05` §8, três níveis + formulação defendida |
| anexo `MUTACORE _ RIC.md` (analisar) | `docs/06` inteiro — E7–E9, 18 vereditos, provas |

### 4.5 Decisões de método que atravessam o trabalho

1. **Nada é aceito por leitura** — regra nascida no ciclo MutaCore, agora em
   `docs/00` §Convenções e `docs/07` §3.
2. **Resultado nulo publicado com a mesma proeminência** do positivo (critério de
   pronto, `docs/04`).
3. **Os números publicados não mudam silenciosamente** — 27 testes de regressão e
   CI em duas plataformas.
4. **I/O e telemetria fora do núcleo** — simulação determinística e testável.
5. **Toda afirmação com critério de aceite** ("pronto é quando…") — `docs/04`.

## 5. Limitações reconhecidas (e onde estão)

- **Quatro limites do README:** mundo roteirizado (L1) · feedback de si, não de
  outrem (L2/L3) · exploratório, sem pré-registro/IC/teste de hipótese ·
  `text_to_digits` perde bytes nulos iniciais.
- **`docs/05` §7:** nenhum número com IC; E6 com **uma única semente**; ninguém lê
  ninguém; hiperparâmetros não varridos; métrica trocada pós-hoc; bug do E5.
- **`docs/06` §10:** a análise cobre só o que está **escrito**; o E7 isola o efeito
  nos níveis (sem recalcular valência); a força bruta varre `[0,1)`.
- **`docs/02` A2(b) / A5:** histerese de τ e forma canônica do grafo **ainda
  abertas** (P1.8 / P1.5).

## 6. Estado atual e fila

- **Repositório:** `github.com/ebiossanto/IA-RESEARCH-MUTARIC` (**público**, `main`);
  CI verde em Windows e Ubuntu (27/27); 5 commits.
- **Código:** 6 módulos (`mundo`, `glifo`, `residuo`, `agente`, `homeostase`,
  `experimentos`) + `tests/` (27) + `run_all.py`.
- **Saídas:** 8 figuras em `figs/`, `resultados/resultados.json` (determinístico,
  só a medição de tempo `E9.segundos` varia entre máquinas).
- **Documentos:** `docs/00` a `docs/08` (nove), `README.md` (PT) e `README.en.md`.
- **Fila:** P1.1 baseline séria → P1.2 teste de hipótese → P1.3 transformações
  perceptivas → P1.4–P1.8 → P2.1 `teoa/core.py` de verdade → P2.3 loop de dois
  agentes → P3 publicação. Pendências externas: repo PIXEL, licença.
- **Como retomar:** `docs/07_continuidade.md`.

## 7. Números publicados — mapa rápido das chaves

| chave | o que |
|---|---|
| `tau`, `varredura_tau_validacao` | τ=0,7 escolhido na validação |
| `transformacoes` | E1/E2/E4: 7 condições × 9 métricas (limpo, ruído σ×4, brilho, descalibração, desfoque) |
| `permutacao_corpo` | E1 sob permutação: relacional 0,193 → 0,666 (canonicalizado) |
| `carga_capacidade` | E3: 5 `d_min` × condições (bits × acurácia) |
| `carga_permutacao`, `carga_isomorfismo` | E3: 0,117 / 0,208 (artefato) / **1,000** |
| `curva_sigma` | leitores × σ (0,0–0,4): duro × robusto |
| `E5_residuo` | A/B/C: classe, carga, ordinal, linhas ocupadas |
| `E6_agencia` | mão dupla, Landauer, τ, reatividade (inclui `tau_medio_landauer_off`) |
| `E7_residuo_mutacore` | reprodução do JSON + dose-resposta γ |
| `E8_sobrevivencia` | reprodução, limites analíticos, ablação, varredura, regime letal |
| `E9_chave_residuo` | espaço de chave, bits, força bruta |
| `demo_mensagem` | "Ganhei!" end-to-end |

---

## Summary (EN)

**What this is:** the full history of the `ricemotions` bridge between the TEOA
project (*why/when* an emotion arises) and the PIXEL/RIC project (*what* can be
recovered from a state written as pixels): episode → valence → 48×32 glyph →
relational reading of family, provenance and a 5.36-bit payload.

**Chronology (all on 04/10/2026):** cycle 0 was an unpackaged folder with a space
in its name and no tests; cycle 1 (`389272a`) made it an importable package with
21 tests and docs 01–04; cycle 2 (`fdf6203`) added E5 (residue), E6 (two-way
agency) and the noise-robust reader (`docs/05`), closing P0.1–P0.4 and
incorporating the user's three requests (Landauer filter, τ as mood, residue
isomorphism); cycle 3 (`8800c9f`) analysed the attached MutaCore/RIC document
against numerical evidence (`docs/06`, E7–E9, 18 verdicts, tests → 27); cycle 4
(`d88ef3f`) published the repository `ebiossanto/IA-RESEARCH-MUTARIC` with CI
green on Windows + Linux; cycle 5 organised the docs (index, continuity, this
report) and ran a consistency audit.

**Studies (E1–E9 plus the σ curve):** provenance in relations (0.919 vs 1.000
baseline — the relational code does *not* win on accuracy, it wins on affine
invariance); family by level vs polarity (polarity = copied label); payload
capacity vs robustness (7.67 bits → 0.580 at σ=0.40 vs 2.58 bits → 0.927);
full pipeline; σ curve (hard reader 0.338 → robust 0.733 at σ=0.10); residue with
three destinations (symmetry recovers 1.000 with 0 rows); two-way agency
(0.00615 closed vs 0.00000 open; exhaustion = −60 % of new relations); MutaCore
residue reproduced to 8.7e-7 but numerically inert (max |Φ| = 0.021 = 10.4 % of
the signal); survival benchmark measuring nothing (0 % gain, death structurally
impossible; dynamic S\* **costs** 20.6 cycles while early recharging **gains**
36); and a residue-keyed cipher with only 16.61 bits of key space (brute force in
≈0.3 s).

**Direction changes:** six external refusals (PIXEL repo not found, cipher,
"Layer-3" validation, always-on telemetry, Walsh spreading, rewriting the data
generator), seven internal refutations (A1–A7, including "the relational code
loses to a trivial baseline" and two real bugs), mid-course redefinitions
(reactivity metric changed after seeing the data; the first E5 approach failed at
25 %; a sampling bug corrected 0.983 → 0.933), and five standing method rules
(nothing accepted without numerical reproduction; null results published as
prominently as positive ones; no silent change to published numbers; I/O and
telemetry outside the core; acceptance criteria for every item).

**Now:** 5 commits, 27 tests, 9 documents, 8 figures, CI green; the queue is P1
(baselines + bootstrap CIs + perceptual transformations) then P2 (the real TEOA
core). Resume with `docs/07_continuidade.md`.
