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

## 2. Cronologia — ciclos 0–9 em um dia (04/10/2026) e ciclo 10 (05/10/2026)

| ciclo | commit | o que mudou |
|---|---|---|
| **0** (pré-repositório) | — | pasta `files ricemotions` com **espaço no nome** (impedia `python -m`), imports relativos que quebram, `../figs` implícito, **zero testes**, E1–E4 soltos |
| **1** | `389272a` | reorganização: pacote `ricemotions/` importável, imports absolutos, `RAIZ/figs`, **21 testes**, `README`/`README.en`, `docs/01`–`docs/04`; números **não alterados** |
| **2** | `fdf6203` | **E5 resíduo, E6 agência, leitor robusto** (`docs/05`); fecha P0.1–P0.4; incorpora os 3 pedidos do usuário (Landauer, τ, isomorfismo); testes 21 |
| **3** | `8800c9f` | **ciclo MutaCore**: análise do anexo `MUTACORE _ RIC.md` com provas (`docs/06`), `homeostase.py`, E7–E9, testes 21 → **27**, `figs/mutacore.png` |
| **4** | `d88ef3f` | **GitHub + CI**: repositório `ebiossanto/IA-RESEARCH-MUTARIC` (privado na época; **tornado público** em 04/10/2026), `.github/workflows/ci.yml` (Windows + Linux, 27/27), badge, revisão de consistência (P0.5 fecha) |
| **5** | `d29ac4c` | **organização final**: `docs/00` (índice), `docs/07` (continuidade), `docs/08` (este), auditoria de consistência entre documentos, chave `tau_medio_landauer_off` no JSON (ajustes seguintes: `abfe920`, `b2d0759`) |
| **6** | `742a811` | **ciclo MUTARIC ev** (`docs/09`): auditoria externa analisada com provas — 5 correções adotadas (2 redacionais no código/docs, 2 viram **P1.9**/**P2.6**), **E10** (paridade de orçamento, 3/3 condições), coleta **real** desta máquina (`maquina.json`, `telemetria_real.json`), testes 27 → **30**, figuras 8 → **9** |
| **7** | `23572f4` | **ciclo MUTARIC ev 2** (`docs/10`): segunda auditoria externa executada e reproduzida (**58/58 números**) — **E10b** (controles fortes de memória, 24 bits, ID + OOD) portado com veredito nulo publicado (*o resíduo não vence memórias fortes*), limitação do comparador no `docs/09` §7.6, novas pendências **P1.10**/**P2.7**, testes 30 → **32**, figuras 9 → **10** |
| **8** | — | **ciclo MUTARIC ev 3/4** (`docs/11`): terceira auditoria externa executada e reproduzida (**JSON idêntico, 0 diferenças em 129 números; 113/113 checagens**) — **E10d** (adversarial + atacante neural, 24 bits) portado com dois vereditos publicados (*o treinamento adversarial reduz reconstrução neural sem custo, mas perde para todos os controles fortes* — H4 refutada; e a **ressalva própria** de que os ataques lineares deles são degenerados — uint8), E10c/E10e **sem código** (não reproduzíveis), nova pendência **P1.11** + atualização de **P2.7**, testes 32 → **34**, figuras 10 → **11** |
| **9** | — | **ciclo MUTARIC ev 5/6** (`docs/12`): quarta auditoria externa — zip **só com saídas, sem código** → **286/286 checagens aritméticas** (tabelas × JSON × CSV, fórmulas de P, Pareto recalculado, Welch/z do ev 6 recalculados com `scipy`) + **replicação NOSSA** `E10e_repl` executada **neste terminal** com as mesmas 200 sementes do ev 5 (163,6 s, pareada por semente) — vereditos: *Pareto ID deles **contido** no nosso; Pareto OOD exato **não repetido** (mesma prateleira P = 1); λ = 1 vaza mais **confirmado** com o pareado que o ev 6 não pôde fazer*; `docs/04` ganhou o **registro detalhado de erros, acertos e retomadas de caminho** (ciclos 0–9); testes 34 → **36**, figuras 11 → **12** |
| **10** (atual) | — | **objetivo novo: sistema JEV-IA-MUTARIC** — material externo `_MUTARIC Jev.md` (fora do repo, mesma pasta das auditorias) analisado e adotado como **P4** no `docs/04`: Jev como **camada probabilística de decisão** sobre o estado MUTARIC (*LLM explica · Jev decide · MUTARIC regula*), contrato `MUTARIC Decision State`, experimento **`E11-JEV`** (4 condições πA–πD, 12 métricas, H1–H4 reescritos com IC pareada e ε declarado), **atacante semântico** (estende P1.11) e **calibração ECE/Brier** — **nenhuma alegação sobre o Jev verificada** (sem acesso ao modelo; as 7 recusas da §9 do documento viraram regra) e **nenhum número novo**: 36 testes, 12 figuras inalterados |

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
| **E5** | o mesmo estado residual em três codificações? | espalhado × banda × simetria (720 permutações), 300 glifos | A: classe **0,270**, resíduo **0,000**, 0 linhas · B: **0,933/0,837**, resíduo **0,977**, 6 linhas · C: **0,303/0,837**, resíduo **1,000**, **0 linhas**; custo da canonicização **0,933→0,837** (**`E5_residuo`**) |
| **E6** | a leitura realimenta as PRÓPRIAS regras? | 3 agentes (aberto × Landauer × sem Landauer) + critério de mão dupla | critério **0,00000** aberto × **0,00615** fechado; tensão **0,248→0,522**; τ **0,700→0,828**; `S*` desvio **+0,250→+0,020**; exaustão: ganhos **0,067→0,027 (−60%)** (**`E6_agencia`**) |
| **E7** | o resíduo MutaCore reproduz o JSON? e a previsão vale? | reprodução + dose-resposta γ=0,8/×10/×100 com controle | dif. máx. **8,7·10⁻⁷**; \|Φ\|máx **0,021 = 10,4%** do sinal; γ=0,8 Δ=**+0,006** (nulo); γ×10 **−0,051** nível × **−0,007** relacional; carga **0,000** (**`E7_residuo_mutacore`**) |
| **E8** | o benchmark mede emoção? | reprodução fiel + ablação 2×2×2 + varredura + regime letal | 1000×1000 = **0%**; morte impossível (T fixo **0,840 < 0,95**, `E` mín **0,185**); letal: **47,4 ± 5,4** (S\* din) × **68,0** (S\* fixo) × 32,0 ⇒ S\* dinâmico **−20,6 ciclos**, recarregar cedo **+36** (**`E8_sobrevivencia`**) |
| **E9** | a cifra com chave = resíduo tem quantos bits? | varredura de `R_L ∈ [0,1)` passo 10⁻⁵ + força bruta | **100001 chaves = 16,61 bits**; chave `0,03452` recuperada em **≈0,3 s** nesta máquina (3453 candidatos; `segundos` declarado não determinístico — **`E9_chave_residuo`**) |
| **E10** | com orçamento IGUAL, o resíduo supera memória convencional? | 4 agentes (sem memória / ruído / conteúdo / resíduo), 2 regimes de distúrbio, comparação pareada | **3/3 condições**: reconstrói menos conteúdo (RMSE **0,1018** vs **0,0827**), MI excedente **+0,0165 bits** (ruído ≈ 0), J(AR) > J(AM) (**t ≈ 12** e **t ≈ 6**) — mas **AR ≈ A0** (nulo): supera a memória convencional, não a ausência de memória (**`E10_orcamento`**) |
| **E10b** | e contra memórias **fortes** de igual orçamento (24 bits)? | 6 memórias (sem / assinada / magnitude / resíduo quadrático / janela / recorrente aprendido), 200 sementes pareadas, IC bootstrap, ID + OOD | **formulação forte refutada**: o resíduo perde para magnitude (ID **−0,0001272**) e para o recorrente (ID **−0,0001904**, OOD **−0,0003150**; ICs fora de zero); vence só a janela no ID; melhor = recorrente; nenhuma memória recupera o sinal (≈ **0,5**) (**`E10b_controles`**) |
| **E10d** | treinamento adversarial reduz reconstrução neural sem custo? e vence os controles? | gradiente reverso + STE em codificador sigmoidal de 24 bits, λ varrido só na validação (fallback: nenhum atingiu 0,515), atacante neural externo, 160 sementes, IC bootstrap, ID + OOD | **H3 confirmada, H4 refutada**: ΔJ **+2,4018×10⁻⁵** ID / **+3,8618×10⁻⁵** OOD com ICs estritamente positivos e neural 0,556→0,522 / 0,580→0,555; mas perde para os 4 controles fortes nos dois splits (ICs negativos, ~0% de vitórias); ressalva própria: ataques lineares **degenerados** (uint8, linear == quadrático em 9/9) (**`E10d_controles`**) |
| **E10e_repl** | as alegações do E10e (ev 5/6) valem numa implementação **independente**, com as mesmas 200 sementes deles? | replicação nossa do protocolo de Pareto: 8 λ × ID/OOD, sementes 70000–70199 do ev 5, atacante neural (2 inits), **pareado por semente** com IC bootstrap, 163,6 s | Pareto ID **{0,1; 0,3; 1}** (**contém** o deles {0,3; 1}); Pareto OOD **{0,01}** vs deles {0,003} — mesma prateleira P = 1, **ponto exato não repetido**; λ = 1 melhor score ID **−0,00362529** e pior privacidade nos 4 cantos; pareado: ΔA OOD **+0,00615** IC [0,00460; 0,00767] > 0, ΔJ ID **+4,38×10⁻⁶** / OOD **−1,20×10⁻⁵** (ICs fora de zero) (**`E10e_repl`**) |

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
- **Ciclo 6 (`docs/09`):** verificação externa da auditoria **MUTARIC ev** —
  5 correções adotadas (a de "mesma energia" virou "três codificações do mesmo
  estado residual"; a de pseudorreplicação virou **P1.9**; a do evento sintético
  virou **P2.6**), a proposição `F(X,R) ≠ F(X,R')` confirmada nos testes, o
  **E10** implementado (orçamento igual, 3/3 condições + ressalva AR ≈ A0) e a
  coleta **real** desta máquina em arquivos próprios não regressados.
- **Ciclo 7 (`docs/10`):** verificação externa da segunda auditoria
  **MUTARIC ev 2** — o `e10b.py` deles executado aqui (**58/58 números
  reproduzidos**) e portado como **E10b**; veredito nulo publicado com a mesma
  proeminência (*contra memórias fortes de igual orçamento o resíduo não
  vence*), o comparador fraco virou limitação escrita (`docs/09` §7.6), a
  parte não fornecida (`e10.py`, testes) ficou **não verificável**, e da
  auditoria saíram **P1.10** e **P2.7**.
- **Ciclo 8 (`docs/11`):** verificação externa da terceira auditoria
  **MUTARIC ev 3/4** — o `e10d.py` deles executado aqui (JSON publicado
  **idêntico**) e portado como **E10d**; dois vereditos publicados com a
  mesma proeminência (H4 refutada: *o adversarial perde para todos os
  controles fortes*; e a **ressalva própria** de que os ataques lineares
  deles são degenerados por uint8 — H1 confirmada com ressalva), E10c/E10e
  **sem código** (só checagem aritmética interna), e da auditoria saíram
  **P1.11** (atacante neural/temporal nos nossos estados) e a atualização
  de **P2.7** (a versão linear de não reconstrução já deu nulo lá fora).
- **Ciclo 9 (`docs/12`):** verificação externa da quarta auditoria
  **MUTARIC ev 5/6** — o zip veio **só com saídas, sem código**, então a
  regra virou dois braços: **286/286 checagens aritméticas** (tabelas ×
  JSON × CSV, fórmulas, Pareto recalculado, Welch/z do ev 6 recalculados
  com `scipy`) e **replicação própria declarada** — `E10e_repl`, o
  protocolo descrito rodado **neste terminal** com as mesmas 200 sementes
  do ev 5, pareado por semente. Vereditos publicados com a mesma
  proemência dos confirmados: *o Pareto ID deles está **contido** no
  nosso; o Pareto OOD exato **não se repetiu** (mesma prateleira P = 1,
  ponto diferente); λ = 1 confirmado como melhor score ID e pior em
  privacidade; maior vazamento OOD de λ = 1 confirmado com o **teste
  pareado que o ev 6 não pôde fazer** (ele não salvou o dado por semente)*.
  O `docs/04` ganhou o **registro detalhado de erros, acertos e retomadas
  de caminho** dos ciclos 0–9.
- **Ciclo 10 (05/10/2026):** material externo `_MUTARIC Jev.md` → **objetivo
  novo P4, sistema JEV-IA-MUTARIC** (Jev decide, MUTARIC regula) com o
  experimento **`E11-JEV`** (πA–πD, 12 métricas, H1–H4) protocolado em
  `docs/04`: contrato puro `decision_state()`, harness rodando **sem** Jev
  (decisor local), atacante semântico (estende P1.11), calibração ECE/Brier —
  nenhuma alegação externa sobre o Jev verificada (sem acesso) e **nenhum
  número novo**.

## 4. Mudanças de direção

### 4.1 Recusas externas (com prova registrada)

| direção proposta | por que não foi seguida | onde |
|---|---|---|
| repositório **PIXEL** como referência | pasta vazia e nenhum repo "pixel" na conta — **não localizado**; 4 correspondências ficam em aberto | `docs/03` §5, lacuna L7 |
| **cifra por resíduo** do MutaCore (§F) | chave de **16,6 bits**: força bruta em ≈0,3 s; incorporar daria *impressão* de canal seguro inexistente | `docs/06` §5, §9 |
| **benchmark de sobrevivência** como "Camada 3" (§E) | métrica **constante** nos parâmetros publicados (0% de ganho, morte impossível); em regime letal mede a **política de recarga**, não a emoção — E6 continua sendo o experimento de agência válido | `docs/06` §4, §9 |
| **telemetria `psutil` ligada por padrão** | I/O e não-determinismo no núcleo quebrariam a reprodutibilidade; fica `homeostase.telemetria()` opcional e a coleta **opt-in** `--telemetria` (arquivos próprios, nunca regressados — `docs/09` §6) | `docs/06` §9, `docs/01` §6 |
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
3. **Os números publicados não mudam silenciosamente** — 36 testes de regressão e
   CI em duas plataformas; campos não determinísticos são **declarados**
   (`E9.campos_nao_deterministicos`, `docs/09` §3).
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
- **`docs/09` §7 (E10):** uma política única para todos os agentes limita o uso
  do conteúdo por AM; MI por histograma de 5 bins com piso embaralhado único;
  ambiente (blocos, β, ε) escolhido por nós; **AR ≈ A0** é um resultado nulo
  de primeira ordem; a carga real desta máquina (~0,55) ficou perto da
  normalização; e (nova, §7.6) **o comparador AM é fraco** — o E10b externo
  mostrou que com memórias fortes de igual orçamento o resíduo não vence
  (`docs/10`).
- **`docs/10` §6 (E10b):** a parte 1 do documento (`e10.py`, 120 sementes) e
  os arquivos de teste deles **não foram fornecidos** e ficam não verificáveis;
  os 78 pesos do recorrente estão **fora** dos 24 bits (declarados: estado
  mutável igual, parâmetros livres); o peso 0,08 do esforço no score é grau de
  liberdade sem análise de sensibilidade; o decodificador é simples ("≈ acaso"
  vale para *esse* decodificador); o ambiente deles é sintético (hot-spots de
  variância) e a refutação vale dentro dele — a ponte com o nosso é **P1.10**.
- **`docs/11` §6 (E10d):** E10c e E10e vieram **sem código** — nada deles é
  reproduzível por execução (só checagem aritmética interna); E10e é
  exploratório por construção (24 sementes, λ inspecionados no teste —
  limitação declarada pelos próprios autores); H4 refuta o **codificador**
  do E10d (sigmoidal + STE + gradiente truncado), não a técnica adversarial;
  e a ressalva do decodificador do E10b ganhou evidência externa — os testes
  lineares do E10d são degenerados (uint8), o que torna **P1.11** (atacante
  neural/temporal nos nossos estados) uma pendência explícita.
- **`docs/12` §2/§6 (E10e_repl):** sem código deles, a replicação **não é**
  reprodução dos números do ev 5/6 — é implementação independente que testa
  alegações (inicialização, otimizador e ataques são escolhas nossas,
  declaradas); o Pareto OOD exato deles **não se repetiu** aqui; e o
  protocolo deles descumpriu 5 de 7 pontos (λ não fixado antes do teste,
  sem ICs, sem dado por semente, sem atacante temporal — ninguém rodou).
- **`docs/02` A2(b) / A5:** histerese de τ e forma canônica do grafo **ainda
  abertas** (P1.8 / P1.5).

## 6. Estado atual e fila

- **Repositório:** `github.com/ebiossanto/IA-RESEARCH-MUTARIC` (**público**, `main`);
  CI verde em Windows e Ubuntu (36/36); histórico completo em `git log` (11 ciclos, §2).
- **Código:** 6 módulos (`mundo`, `glifo`, `residuo`, `agente`, `homeostase`,
  `experimentos`) + `tests/` (36) + `run_all.py`.
- **Saídas:** 12 figuras em `figs/`, `resultados/resultados.json` (determinístico;
  `E9.segundos` está declarado em `campos_nao_deterministicos` e varia entre
  máquinas), `resultados/maquina.json` + `resultados/telemetria_real.json`
  (coleta real, `deterministico: false`, nunca regressada).
- **Documentos:** `docs/00` a `docs/12` (treze), `README.md` (PT) e `README.en.md`.
- **Fila:** P1.1 baseline séria → P1.2 teste de hipótese → P1.3 transformações
  perceptivas → P1.4–P1.11 (novos: protocolo hierárquico, **controles fortes
  de memória no E10** e **atacante neural/temporal nos nossos estados**) →
  P2.1 `teoa/core.py` de
  verdade → P2.3 loop de dois agentes → P2.6 (novo: agente sem evento externo)
  → P2.7 (E10c, resíduo preditivo com não reconstrução — já com penalidade
  adversarial, `docs/11` §5) →
  P3 publicação → **P4** (objetivo novo 05/10/2026: sistema **JEV-IA-MUTARIC**,
  experimento `E11-JEV` — `docs/04`). Pendências externas: repo PIXEL, licença,
  acesso ao Jev (P4.3/P4.4 bloqueados sem ele).
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
| `E9_chave_residuo` | espaço de chave, bits, força bruta (`segundos` = não determinístico, declarado) |
| `E10_orcamento` | E10: J pareado (2 regimes), RMSE de reconstrução, MI excedente, 3 condições, `veredito` |
| `E10b_controles` | E10b: scores/perdas das 6 memórias (ID + OOD), Δ pareados com IC bootstrap, decodificação, `melhor_score` |
| `E10d_controles` | E10d: varredura de validação + `lambda_escolhido` (fallback), sem/com adversário (ID + OOD) com Δ e IC, 4 comparadores fortes, ataques linear/quadrático/neural |
| `E10e_repl` | réplica do protocolo Pareto: pontos ID/OOD (score, neural, P, execuções), fronteiras, teste pareado por semente (utilidade + atacante, com IC) e `comparacao_ev5_ev6` |
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
report) and ran a consistency audit; cycle 6 (`docs/09`) verified the external
audit "MUTARIC ev" claim by claim — five corrections adopted, E10 built, real
machine telemetry collected (tests → 30, figures → 9); cycle 7 (`docs/10`)
verified the second audit "MUTARIC ev 2" by **execution** — its `e10b.py` run
here with **58/58 numbers reproduced** and ported as E10b, refutation of the
strong claim published as a null result, comparator weakness written into
`docs/09` §7.6, new queue items P1.10/P2.7 (tests → 32, figures → 10);
cycle 8 (`docs/11`) verified the third audit "MUTARIC ev 3/4" by **execution**
— its `e10d.py` run here regenerating the published JSON **identical (0
differences in 129 numbers)** and ported as E10d, two verdicts published with
equal prominence (H4 refuted: *the adversarial variant loses to every strong
control*; plus our own caveat that their **linear attackers are degenerate**
(uint8 wraparound), so H1 stands only with that caveat), E10c/E10e shipped
**without code** (unverifiable by execution), new queue item P1.11 and P2.7
updated (tests → 34, figures → 11); cycle 9 (`docs/12`) handled the fourth
external package "MUTARIC ev 5 / ev 6" — shipped **outputs only (JSON, CSV,
PNG), no code** — with **286/286 arithmetic checks** (document × JSON × CSV,
privacy formulas, Pareto frontiers recomputed, Welch and z-tests recomputed
with `scipy`) plus **our own replication of the protocol executed on this
terminal** (`E10e_repl`, the same 200 seeds, paired per seed): their ID
Pareto {0.3; 1} **is contained in ours**, **their exact OOD Pareto did not
repeat** (same P = 1 plateau, different point — published with equal
prominence), and λ = 1's larger OOD leakage was confirmed with the **paired
test ev 6 could not run** (tests → 36, figures → 12; `docs/04` also gained
a detailed record of errors, successes and course changes for cycles 0–9).
Cycle 10 (05/10/2026) registered a **new objective without new numbers**: the
**JEV-IA-MUTARIC system** from the external `_MUTARIC Jev.md` — Jev as a
probabilistic decision layer over the MUTARIC state (*LLM explains · Jev
decides · MUTARIC regulates*) with the **`E11-JEV`** experiment (4 conditions,
12 metrics, H1–H4 with paired-CI acceptance) adopted as **P4** in `docs/04`,
including a semantic attacker (extending P1.11) and ECE/Brier calibration;
**no claim about Jev was verified** (no access to the model) and its §9
caveats became project rules.

**Studies (E1–E10 + E10b + E10d + E10e_repl plus the σ curve):** provenance in relations (0.919 vs 1.000
baseline — the relational code does *not* win on accuracy, it wins on affine
invariance); family by level vs polarity (polarity = copied label); payload
capacity vs robustness (7.67 bits → 0.580 at σ=0.40 vs 2.58 bits → 0.927);
full pipeline; σ curve (hard reader 0.338 → robust 0.733 at σ=0.10); residue with
three destinations (symmetry recovers 1.000 with 0 rows); two-way agency
(0.00615 closed vs 0.00000 open; exhaustion = −60 % of new relations); MutaCore
residue reproduced to 8.7e-7 but numerically inert (max |Φ| = 0.021 = 10.4 % of
the signal); survival benchmark measuring nothing (0 % gain, death structurally
impossible; dynamic S\* **costs** 20.6 cycles while early recharging **gains**
36); a residue-keyed cipher with only 16.61 bits of key space (brute force in
≈0.3 s); and **E10**, the equal-budget comparison — 3/3 conditions hold (less
content than conventional memory, +0.0165 bits of excess MI, paired J(AR) > J(AM)
with t ≈ 12 and t ≈ 6) **but AR ≈ A0**: the residue beats conventional memory,
not the absence of memory (published as a partial null result); and **E10b**,
the strong-control replication — against magnitude EMA, short window and
learned recurrent state at equal 24-bit budget the residue **loses** in both
splits (CIs exclude zero, best agent = learned recurrent), so the strong
formulation is refuted in that environment (published as a null result too);
and **E10d**, the adversarial replication — adversarial training with a
straight-through encoder **does** reduce neural reconstruction without cost
within its own architecture (ΔJ > 0 with strictly positive CIs in both
splits, neural attacker 0.556 → 0.522 ID and 0.580 → 0.555 OOD) **but loses
to every strong E10b control** (H4 refuted; all CIs negative, ≈0 % wins),
and our verification found their linear/quadratic attackers **degenerate**
(uint8 wraparound: targets {255,1}, linear == quadratic in 9/9 comparisons),
which is why H1 is accepted only with that caveat; and **E10e_repl**, our
replication of the Pareto protocol on the same 200 seeds — their ID Pareto
contained in ours, the exact OOD Pareto point **not repeated** (published as
such), λ = 1's leakage confirmed with the paired per-seed bootstrap.

**Direction changes:** six external refusals (PIXEL repo not found, cipher,
"Layer-3" validation, always-on telemetry, Walsh spreading, rewriting the data
generator), seven internal refutations (A1–A7, including "the relational code
loses to a trivial baseline" and two real bugs), mid-course redefinitions
(reactivity metric changed after seeing the data; the first E5 approach failed at
25 %; a sampling bug corrected 0.983 → 0.933), and five standing method rules
(nothing accepted without numerical reproduction; null results published as
prominently as positive ones; no silent change to published numbers; I/O and
telemetry outside the core; acceptance criteria for every item).

**Now:** 36 tests, 13 documents, 12 figures, CI green; the queue is P1
(baselines + bootstrap CIs + perceptual transformations, plus the new P1.9
hierarchical protocol, P1.10 strong memory controls and P1.11 neural/temporal
attackers against our own states) then P2 (the real TEOA core, plus P2.6/P2.7 —
P2.7 already escalated to an adversarial penalty after the linear version came
out null in the external E10c). Resume with
`docs/07_continuidade.md`.
