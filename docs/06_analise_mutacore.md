# 06 — Análise do documento MutaCore/RIC

Este documento analisa o arquivo **`MUTACORE _ RIC.md`** (anexo enviado pelo usuário,
fora do repositório), que propõe seis blocos:

| Bloco | Conteúdo |
|---|---|
| A | Análise crítica do trabalho atual (o que é bom, o que é ruim, próximos passos) |
| B | Formalismo do "resíduo de Landauer" `ΔH_L` injetado na dinâmica dos episódios |
| C | Homeostase por telemetria **real** de hardware (`psutil`) → alvo `S*` e limiar `τ` |
| D | Política de alocação de recursos (audaciosa × conservadora) pela distância a `S*` |
| E | Benchmark de sobrevivência: robô afetivo × robô linear em 1000 ciclos |
| F | Cripto-esteganografia: cifra de fluxo cuja chave é o resíduo térmico |

**Método.** Nenhuma afirmação foi aceita por leitura: cada uma foi **reproduzida
numericamente** antes. O que passou virou código; o que não passou ficou registrado
com a prova. Números em `resultados/resultados.json` (chaves `E7_residuo_mutacore`,
`E8_sobrevivencia`, `E9_chave_residuo`), figura em `figs/mutacore.png`, código em
`ricemotions/homeostase.py` + `experimentos.e7/e8/e9`, testes **27/27**.

Reprodução integral: `python run_all.py`.

---

## 1. Veredito afirmação a afirmação

| # | Afirmação do documento | Veredito | Prova |
|---|---|---|---|
| 1 | `ΔH_L = γ·Σ QW_i·|X_i(t)−X_i(t−1)|²` com acúmulo `R_L = (1−α)R_L + ΔH_L` é um formalismo aplicável aos episódios (§B) | **Correto e reproduzível** | §3 |
| 2 | O JSON publicado (`max_residual_stress = 0,029968` etc., γ=0,8, α_L=0,15) | **Confirmado** | §3 — dif. máx. 8,7·10⁻⁷; teste `test_reproduz_o_json_do_mutacore` |
| 3 | O código da §B ("cole isto dentro de `mundo.py`") injeta esse resíduo | **Incorreto: é inerte** | §8.1 — `R_L ≡ 0` por construção |
| 4 | `Φ` altera os canais "de forma sutil, mas profunda" | **Sutil sim, profunda não** | §3 — \|Φ\|máx = 0,021 = 10,4% do sinal; ΔT final = 0,0022 = 0,2% da escala. Nosso E6 dá ΔT = **+0,274** |
| 5 | Com resíduo injetado, "`6c_nivel` sofrerá penalidade mensurável" | **Não nos parâmetros publicados** | §7 — Δ = +0,006 (nem sinal negativo) |
| 6 | "`6c_relacional` mantém a estabilidade macro" | **Verdadeiro só a partir de γ×10** | §7 — γ×10: −0,007 relacional × −0,051 nível (7× mais resiliente); γ×100: ambos colapsam |
| 7 | "Ruído σ ≤ 0,30 … mantendo a acurácia em **~91,8%**" (§1 do documento de continuidade) | **Falso para ruído; verdadeiro só para afins** | §6 — leitor duro 0,167 em σ=0,30 (acaso = 1/6); ponderado 0,391 |
| 8 | Carga com `d_min` baixo "despenca drasticamente" em σ=0,40 | **Correto** | §6 — 0,580 (`d_min=1`) × 0,927 (`d_min=8`) |
| 9 | Canonicalização "sobrevive a permutações totais (720) … sem perda de dados" | **Parcial** | §6 — corpo 0,193 → **0,666** (limpo é 0,919: há perda). "Sem perda" vale só para a **carga** com codebook de isomorfismo (1,000) |
| 10 | "SUCESSO DA CAMADA 3: sobrevida X% maior" (§E) | **Não se mede — e não pode ser medido nos parâmetros dados** | §4 — 1000 × 1000 = 0,0%; morte estruturalmente impossível |
| 11 | `S*` dinâmico = "auto-preservação (mão dupla)" | **Refutado pela ablação** | §4 — em regime letal o `S*` dinâmico **custa** 20,6 ciclos; o que salva é recarregar cedo |
| 12 | "Quem não souber o histórico térmico não consegue descriptografar" (§F) | **Incorreto: 16,6 bits de chave** | §5 — força bruta recupera a chave em ≈0,3 s |
| 13 | Espalhamento por Walsh torna a carga "imune a brilho, desfoque e ruído" | **Não verificável** | §8.5 — não existe decodificador e `landauer_stress` nunca é usado |
| 14 | Telemetria → `S*` e `τ` (§C) | **Correto — incorporado** | §2 |
| 15 | Política `DEFENSIVA`/`EXPLORATORIA` pela distância a `S*` (§D) | **Correto — incorporado** | §2 |
| 16 | Coleta de telemetria com `psutil` | **Correto com duas correções** | §8.3 |
| 17 | "O resíduo é a memória de curto prazo do sistema" (§A, lado bom) | **Correto — já implementado aqui** | `docs/05` §5 (E5) e §6 (E6) |
| 18 | Três próximos passos da §A (filtro de Landauer, modularização de τ, isomorfismo de resíduo) | **Já implementados** — não são próximos passos pendentes | `docs/05` §3–§5 |

**Balanço das 18 afirmações: 8 confirmadas** (1, 2, 8, 14, 15, 16, 17, 18) ·
**6 refutadas** (3, 5, 7, 10, 11, 12) · **4 parciais ou não verificáveis**
(4, 6, 9, 13).

---

## 2. O que entrou no código

| Mecanismo do documento | Onde ficou | Teste |
|---|---|---|
| Resíduo endógeno `ΔH_L` → `R_L` → `Φ` (§B) | `homeostase.residuo_transicao`, `sensibilidade`, `injetar`, `simular_landauer` | `test_reproduz_o_json_do_mutacore` |
| Telemetria → `S*` (§C) | `homeostase.fator_termico`, `S_star_homeostatico` | `test_homeostase_regras` |
| Telemetria → `τ` (§C) | `homeostase.tau_carga` + **`Agente.passo(..., carga_hw=)`** — entra no `τ` pelo mesmo caminho do resíduo | `test_carga_da_maquina_sobe_o_tau` |
| Política pela distância a `S*` (§D) | `homeostase.politica` | `test_homeostase_regras` |
| Robô do benchmark (§E) | `homeostase.passo_robo` com **três interruptores separados** (`dinamico`, `generosa`, `esfria`) — o documento mistura os três num só rótulo "afetivo" | `test_benchmark_mutacore` |
| Medição/força bruta (§E, §F) | `experimentos.e8_sobrevivencia`, `e9_chave_residuo` | `test_chave_acoplada_ao_residuo_e_bruteforceavel` |
| Coleta de telemetria real | `homeostase.telemetria()` — **opcional** (`psutil`), nunca usada em teste nem em experimento | — |

Duas decisões de projeto:

1. **`carga_hw` é externa e opcional.** Com o padrão `0.0` o agente é bit a bit o
   mesmo de E6 — os números publicados não mudam. A telemetria chega como
   *argumento*; quem mede é o chamador. Isso mantém o núcleo puro e determinístico
   (regra de `docs/01` §6: I/O só em `experimentos.py`).
2. **O resíduo endógeno convive com o nosso.** `residuo.gerar` (sorteio AR(1), usado
   em E5/E6) é *resíduo imposto pelo ambiente*; `homeostase.residuo_transicao` é
   *resíduo produzido pelo que o sistema fez*. São duas origens diferentes da mesma
   grandeza e o trabalho agora tem as duas.

---

## 3. Prova 1 — o JSON é reproduzível, e é inerte

O documento afirma ter rodado o loop com γ=0,8 e α_L=0,15 e publica seis triplas.
Reproduzidas integralmente (diferença máxima **8,7·10⁻⁷**, compatível com o
arredondamento em 6 casas):

| classe | `max_residual_stress` (publ. / reproduz.) | `final_tension_diff` (publ. / reproduz.) |
|---|---|---|
| alegria-meta | 0,029968 / 0,029968 | 0,002241 / 0,002242 |
| alegria-vínculo | 0,010617 / 0,010618 | 0,000977 / 0,000977 |
| alegria-estado | 0 / 0 | 0 / 0 |
| tristeza-meta | 0,026211 / 0,026212 | 0,001988 / 0,001989 |
| tristeza-vínculo | 0,019202 / 0,019203 | 0,001628 / 0,001629 |
| tristeza-estado | 0 / 0 | 0 / 0 |

O formalismo está correto. **O que ele faz, porém, é quase nada:**

| grandeza | valor | referência |
|---|---|---|
| \|Φ\| máximo injetado | **0,021** | escala dos canais = [0,1] |
| amplitude do sinal do roteiro (ΔT em alegria-meta) | 0,201 | — |
| razão deslocamento / sinal | **10,4%** | — |
| `final_tension_diff` no fim do frame | 0,0022 | 0,2% da escala |
| deslocamento que **nosso E6** produz em T | **+0,274** | `E6_agencia` (0,522 vs 0,248) |

Ou seja: o loop do MutaCore é um *perturbador de 2% da escala* (10,4% do próprio
sinal do roteiro), enquanto o ciclo que já existia em `docs/05` produz um efeito
100× maior. A palavra "profunda" da §B não se sustenta; a palavra "sutil", sim.
`figs/mutacore.png` (painel superior esquerdo) mostra `R_L(t)` das quatro classes
com resíduo e a magnitude de Φ anotada.

---

## 4. Prova 2 — o benchmark não mede emoção

### 4.1 Reprodução fiel (1000 ciclos, `np.random.seed(42)`, RNG global como no doc)

| robô | ciclos | metas | E mínimo | T máximo |
|---|---|---|---|---|
| afetivo (S\* dinâmico + política de tensão + esfria 0,10) | **1000** | 215 | 0,440 | 0,599 |
| linear (S\* fixo + `E<0,20` + esfria 0,02) | **1000** | 224 | 0,215 | 0,713 |

`ganho_de_sobrevida_pct = 0,0`. A linha
`💡 SUCESSO DA CAMADA 3: … sobrevida X% MAIOR` só é impressa **se**
`ciclos_afetivo > ciclos_linear` — logo ela **nunca imprime**. E o robô "afetivo"
atinge *menos* metas (215 × 224), porque passa mais tempo recarregando.

### 4.2 Por que ninguém morre (limite analítico, confirmado numericamente)

| condição de morte | limite dos parâmetros publicados | dá para morrer? |
|---|---|---|
| `T ≥ 0,95` | `dH_L` máx = 0,15·0,8² + 0,05·0,6 = 0,126 → ponto fixo `T = dH/0,15 = 0,840` | **não** |
| `E ≤ 0` | política da tensão recarrega em `E<0,55` (porque `S*_E = 0,8` e `déficit > 0,25`), a rígida em `E<0,20`, ambas `+0,12` → `E` mínimo possível = 0,20 − 0,015 = 0,185 | **não** |

Os dois robôs são termostatos: a política dispara *antes* de o limite ser atingido
e a carga (+0,12/ciclo) é 8× o gasto (0,015/ciclo). **A morte é impossível por
construção**, e portanto a métrica "sobrevida" é constante.

### 4.3 Ablação 2×2×2 nos parâmetros do documento

Separando os três fatores que o documento mistura (`S*` dinâmico × política pela
tensão × intensidade do esfrio), **as 8 combinações sobrevivem 1000/1000**:
nos parâmetros publicados o experimento não discrimina nada. O único indício que
ele deixa aparecer já está na **margem de E**: com `S*` dinâmico o robô termina com
`E` mínimo **0,460**, enquanto com `S*` fixo ele termina com **0,565** — a
homeostase faz o robô recarregar *menos*, ou seja, chega mais perto da morte sem
chegar nela.

### 4.4 Varredura de severidade — o que decide é o gasto, não a emoção

| gasto de energia por ciclo | afetiva (S\* din) | S\* fixo + tensão | rígida (`E<0,20`) |
|---|---|---|---|
| **0,015 (publicado)** | 1000 | 1000 | 1000 |
| 0,10 | 1000 | 1000 | 1000 |
| 0,12 (= carga) | 1000 | 1000 | 1000 |
| 0,125 | 88 | **112** | 64 |
| 0,15 | 19 | **23** | 15 |

A morte começa exatamente quando `gasto > carga (0,12)`. A partir daí **o `S*`
dinâmico piora a sobrevivência** em relação ao `S*` fixo.

### 4.5 Regime letal, 50 sementes (gasto = 0,13)

| configuração | ciclos (média ± desvio) |
|---|---|
| afetivo (S\* dinâmico + tensão) | **47,4 ± 5,4** |
| S\* **fixo** + tensão (ablação do S\*) | **68,0 ± 0,0** |
| linear rígido (`E<0,20`) | 32,0 ± 0,0 |

- **Efeito do `S*` dinâmico: −20,6 ciclos** (piora de 30%).
- **Efeito de recarregar cedo: +36 ciclos** (68 × 32).

O mecanismo é direto: com calor, `S*_E` desce (0,8 → 0,45) e `S*_T` sobe
(0,25 → 0,55), ou seja **os dois limiares ficam mais difíceis de tocar** — o robô
"auto-preservado" recarrega *menos*. A ablação mostra que a sobrevivência vem da
política (recarga antecipada), não da homeostase de `S*`. `figs/mutacore.png`
(painéis inferiores) mostra a varredura e a ablação.

---

## 5. Prova 3 — a chave tem 16,6 bits

O §F cifra dígitos com um keystream de `np.random.default_rng(round(R_L·100000))`
e afirma que só quem conhece o histórico térmico lê a mensagem.

| medida | valor |
|---|---|
| espaço de chave real (`R_L ∈ [0,1)`, passo 10⁻⁵) | 100001 valores |
| entropia | **log₂(100001) = 16,61 bits** |
| força bruta sobre "MutaCore v2" | chave `0,03452` recuperada em **≈0,3 s** nesta máquina após **3453** candidatos (`segundos` é medição não determinística — `docs/09` §3) |
| roundtrip com a chave exata | OK |

Três problemas, em ordem de gravidade:

1. **Não é One-Time Pad.** Um OTP exige entropia de chave ≥ ao texto e uso
   único; aqui a chave é o resultado de `round` de um float numa faixa de 10⁵
   valores, ou seja ~17 bits — abaixo do que se considera brute-forceável.
2. **Sincronização impossível na prática.** O documento exige que receptor e
   emissor conheçam o mesmo `R_L` a 10⁻⁵ (o próprio exemplo usa 0,034521 ×
   0,034500 e chama a diferença de "ataque"); qualquer ruído de canal dessincroniza.
3. **O que fica de bom:** acoplar uma semente ao resíduo é legítimo *se* o espaço
   de chave for grande (ex.: semear um CSPRNG com o float64 completo + epoch) e se
   a sincronização for resolvida. Isso **não** foi incorporado: está fora do escopo
   do trabalho e o mecanismo como escrito não sustenta a alegação de segurança.

Teste: `test_chave_acoplada_ao_residuo_e_bruteforceavel` (o número também está em
`E9_chave_residuo`).

---

## 6. Prova 4 — onde os ~91,8% são verdade

O documento cita `6c_relacional ≈ 91,8%` e o associa a "ruído σ ≤ 0,30,
descalibração de ganho, desfoque e brilho". Os nossos números separam os casos:

| transformação | `6c_relacional` | `6c_nivel` | `carga_acc` |
|---|---|---|---|
| limpo | **0,919** | 0,786 | 1,000 |
| brilho ×0,7 +0,1 | **0,919** | 0,509 | 1,000 |
| descalibração por linha | **0,919** | 0,549 | 1,000 |
| desfoque temporal | **0,898** | 0,786 | 0,957 |
| ruído σ=0,05 | 0,751 | 0,787 | 1,000 |
| ruído σ=0,10 | **0,334** | 0,788 | 1,000 |
| ruído σ=0,20 | **0,172** | 0,776 | 1,000 |

Acaso em 6 classes = 0,167.

- **Verdadeiro:** o RIC é invariante a transformações *afins* (brilho,
  descalibração, desfoque) e mantém 0,898–0,919 — é exatamente o que a correlação
  normalizada prevê. E o **leitor duro** mantém 0,919.
- **Falso:** para **ruído**, o leitor duro vai ao acaso em σ=0,10 (0,334) e fica
  em 0,167 em σ=0,30. Mesmo o leitor **robusto** (novo, `cont_ponderado`) chega só
  a **0,391** em σ=0,30 — acima do acaso, mas longe de 91,8%.

Curva completa do leitor duro × robusto (`curva_sigma`): 0,919/0,892 (σ=0),
0,759/0,794 (0,05), 0,338/0,733 (0,10), 0,194/0,646 (0,15), 0,174/0,544 (0,20),
0,167/**0,391** (0,30), 0,167/0,308 (0,40).

Dois achados *a favor* do documento, medidos aqui:

- **Carga × σ=0,40:** `d_min=1` → 0,580; `d_min=2` → 0,603; `d_min=4` → 0,727;
  `d_min=6` → 0,870; `d_min=8` → 0,927. A afirmação "d_min baixo despenca
  drasticamente" está **correta**, e o efeito é monotônico.
- **Canonicalização sob permutação total:** corpo relacional 0,193 → **0,666**
  (720 permutações), acima do acaso mas abaixo do limpo (0,919) — logo a frase
  "sem perda de dados" está **exagerada** para o corpo. Para a **carga**, o
  `carga_permutacao` dá 0,117 → 0,208 (ambiguidade de isomorfismo, artefato já
  documentado em `docs/02`), e **sem** essa ambiguidade (codebook de isomorfismo)
  a carga sob permutação é **1,000** — aí sim "sem perda".

---

## 7. Prova 5 — a previsão "nível cai, relacional segura" (E7)

O §B prevê que, com resíduo injetado, `6c_nivel` sofra penalidade mensurável e o
canal relacional se mantenha. Teste: injetamos `Φ` nos 300 episódios do conjunto
de teste, re-renderizamos com os **mesmos RNGs** e re-avaliamos com o mesmo
pipeline. O **controle** (re-renderização sem resíduo) dá Δ = 0,000 em todas as
métricas — o caminho de renderização é determinístico, então todo Δ abaixo vem do
resíduo.

| condição | `6c_relacional` | `6c_nivel` | `3c_relacional` | `carga_acc` |
|---|---|---|---|---|
| re-renderização (controle) | 0,000 | 0,000 | 0,000 | 0,000 |
| **γ = 0,8 (publicado)** | +0,001 | +0,006 | −0,002 | 0,000 |
| γ × 10 (resíduo ≈ sinal) | **−0,007** | **−0,051** | −0,068 | 0,000 |
| γ × 100 (destruição) | −0,741 | −0,617 | −0,792 | 0,000 |

Leitura:

1. **Nos parâmetros publicados não há efeito algum** (Δ ≤ 0,006, sem sinal
   confiável). A previsão "penalidade mensurável" **não se confirma** em γ=0,8.
2. **Em γ×10 a previsão se confirma qualitativamente:** o nível cai 7× mais que o
   relacional (−0,051 × −0,007). Ou seja, a intuição do documento está certa, só
   que o parâmetro publicado é ~10 pequeno demais para produzi-la.
3. **Em γ×100** `Φ` ultrapassa a faixa [0,1] e o `clip` destrói o glifo: tudo
   colapsa e o relacional pior que o nível — o regime não é mais de distorção.
4. **A carga explícita não se mexe em nenhuma condição** (Δ = 0,000), coerente com
   `carga_capacidade` (1,000 até σ=0,2).
5. Com γ=0,8 a família afetiva de **297/300** glifos permanece a mesma (98,7%) —
   o resíduo não muda a classe lida.

---

## 8. Bugs e inconsistências do código do documento

1. **O código da §B não faz nada.** Ele calcula
   `delta_info = |X_dynamic[:, t−1] − X_base[:, t−1]|` mas começa com
   `X_dynamic[:,0] = X_base[:,0]` e injeta `Φ` que depende de `R_L`. Por indução:
   `R_L = 0` no passo 1 → `Φ = 0` → `X_dynamic[:,1] = X_base[:,1]` → … →
   `R_L ≡ 0` para sempre. **Verificado: `max R_L = 0,000000`** nas seis classes.
   O JSON publicado só é reproduzido pelo *segundo* código do documento
   (`step_transition_erasure = |X_base[:,t] − X_base[:,t−1]|`), que é o que
   implementamos em `homeostase.residuo_transicao`.
2. **Dois conjuntos de parâmetros incompatíveis** no mesmo documento: o snippet
   usa γ=0,5, α_L=0,2 e λ=[−0,3; 0,4; −0,5; 0; −0,2; 0,25]; o código do JSON usa
   γ=0,8, α_L=0,15 e λ=[−0,25; 0,35; −0,4; 0; −0,15; 0,2]. Só o segundo gera o
   resultado publicado.
3. **`psutil.cpu_percent(interval=None)` devolve 0,0 na primeira chamada** — a
   telemetria inicial do documento lê CPU zerada. Corrigido em
   `homeostase.telemetria` (descarta a primeira amostra e usa `interval=0.1`).
   `psutil.sensors_temperatures` não existe no Windows (`hasattr` → `False`), então
   a temperatura vira **modelo**, não medição — nós declaramos isso no código; o
   documento não.
4. **`if t in:` é erro de sintaxe** — o `validacao_sobrevivencia.py` como escrito
   não roda sem editar.
5. **`encode_payload_layer(digit, landauer_stress, rng)` nunca usa
   `landauer_stress`.** A "modulação Walsh baseada no stress térmico" não existe no
   corpo da função, e não há função de decodificação da camada de Walsh — por isso
   a alegação de imunidade a ruído (§F) é **não verificável** no código deles.
   (Para a carga, o nosso pipeline já mede essa robustez: `carga_capacidade`.)
6. **`text_to_ric_digits` perde bytes nulos iniciais**: `int.from_bytes` descarta
   zeros à esquerda, então `"\x00abc"` → `"abc"`. Roundtrip verificado: falha.
   **O mesmo vale para o nosso `glifo.text_to_digits`** — é a mesma construção —
   e `test_texto_roundtrip` não cobre o caso (testa `"Ganhei!"`, `"emoção"`,
   `"a"`). Achado desta análise, registrado aqui como limitação conhecida das duas
   implementações; corrigir mudaria a codificação dos dígitos e, com ela, números já
   publicados (`demo_mensagem`), então fica documentado em vez de corrigido às
   cegas.

---

## 9. O que **não** entrou

| Proposta | Motivo |
|---|---|
| Cifra por resíduo (§F) como recurso do trabalho | Espaço de chave de 16,6 bits não sustenta a alegação de segurança (§5). Incorporar daria a *impressão* de um canal seguro que não existe. |
| Benchmark de sobrevivência como "Camada 3 de validação" (§E) | A métrica é constante nos parâmetros publicados e, em regime letal, mede a política de recarga, não a emoção (§4). Como validação de agência, `E6` é o experimento válido. |
| Telemetria real ligada por padrão (`psutil`) | I/O e não-determinismo no núcleo quebrariam a reprodutibilidade (`docs/01` §6). Fica como função opcional, nunca chamada por teste ou experimento. |
| Espalhamento por Walsh (§F) | Sem decodificador não há o que testar (§8.5). Ideia correta, mas exige projeto próprio (portadora por patch + decodificador) — candidata a item futuro em `docs/04`. |
| Reescrever `mundo.episode` com o loop de Φ | Alteraria o gerador dos conjuntos de treino/validação/teste e, com ele, **todos** os números publicados. O resíduo do MutaCore vive em `homeostase`, fora do caminho dos dados. |

---

## 10. Limitações desta análise

- A reprodução cobre o que está **escrito** no documento. Se houver código não
  anexado (o texto fala em "simulação matemática isolada" e em resultados de
  `6c_nivel`/`6c_relacional` com resíduo que não vêm com números), ele não foi
  testado — mas também não é verificável.
- O benchmark foi reproduzido fielmente nos parâmetros publicados **e** em três
  variações de severidade. Outros arranjos (por exemplo: recarga com atraso, custo
  de deslocamento, morte por T dependente de carga real) podem produzir curvas de
  sobrevivência diferentes — mas aí são **outros** experimentos, e a afirmação
  original continua não medida.
- O E7 injeta `Φ` no episódio **antes** da renderização, mantendo valência, família
  e símbolo originais para isolar o efeito nas *níveis*. Uma versão em que `Φ`
  muda também a valência (recalculada) teria efeito adicional de reclassificação —
  em γ=0,8 isso atingiria 4 de 300 glifos (1,3%).
- A força bruta varre `R_L ∈ [0,1)`. Resíduos fora dessa faixa ampliariam o espaço
  linearmente, mas continuariam < 2³² seeds e bruteforceáveis; o documento só opera
  nessa faixa.
- Esta análise é sobre o **documento**, não sobre a ideia geral de "emoção com
  procedência". As partes que concordam com o trabalho (resíduo como memória,
  Landauer como filtro, τ como humor, isomorfismo) já estão em `docs/05`.

---

## 11. Summary (EN)

The attached *MutaCore/RIC* document proposes a Landauer-residue formalism, a
hardware-homeostasis layer, a resource-allocation policy, a survival benchmark and
a residue-keyed cipher. **Every quantitative claim was reproduced before being
accepted.**

**Reproduced and adopted**

- The published `R_L` JSON is reproduced exactly (max diff 8.7e-7) → the
  formalism `ΔH_L = γ·ΣQW·|ΔX|²` with `R_L = (1−α)R_L + ΔH_L` is correct.
  Implemented in `ricemotions/homeostase.py` (endogenous residue: it comes from
  what the system *did*, unlike the ambient draw used in E5/E6).
- Telemetry → `S*` and → `τ` are correct and were integrated as **pure functions**
  plus an optional `Agente.passo(..., carga_hw=)` hook (default 0 = published
  behaviour unchanged).
- The policy `DEFENSIVA`/`EXPLORATORIA` based on the *distance to S\** is correct
  and was adopted (`homeostase.politica`).
- The claim that low-`d_min` payloads collapse at σ=0.40 is correct: 0.580
  (`d_min=1`) vs 0.927 (`d_min=8`).

**Refuted or corrected**

- The `91.8 %` robustness claim holds for *affine* transformations (0.898–0.919)
  but **not for noise**: the hard reader is at chance (0.167) at σ=0.30 and the
  robust reader reaches only 0.391.
- The residue injection is numerically **inert**: max |Φ| = 0.021 (10.4 % of the
  script's signal); the code the document tells us to paste into `mundo.py`
  produces `R_L ≡ 0` by construction.
- The prediction "`6c_nivel` drops, `6c_relacional` holds" does **not** hold at the
  published γ=0.8 (Δ ≈ 0); it becomes true at γ×10 (−0.051 vs −0.007) — the
  intuition is right, the published parameter is ~10× too small.
- The survival benchmark reports **0 %** survival gain: both robots live
  1000/1000 cycles because death is structurally impossible (T fixed point 0.840 <
  0.95; minimum reachable E 0.185 > 0), so the "SUCESSO DA CAMADA 3" line never
  prints. Ablation in a lethal regime shows the dynamic `S*` **costs** 20.6 cycles
  while early recharging **gains** 36 — survival comes from the policy, not from
  the homeostasis of `S*`.
- The residue-keyed cipher has **16.61 bits** of key space (100001 possible
  seeds): brute force recovers the message in ≈0.3 s after 3453 candidates. Not a
  one-time pad; not adopted.
- Several code bugs documented (inert residue snippet, two incompatible parameter
  sets, `cpu_percent` returning 0.0 on the first call, `if t in:` syntax error,
  unused `landauer_stress` parameter with no Walsh decoder).

Artifacts: `resultados/resultados.json` (`E7_residuo_mutacore`,
`E8_sobrevivencia`, `E9_chave_residuo`), `figs/mutacore.png`, tests 30/30 via
`python run_all.py`.
