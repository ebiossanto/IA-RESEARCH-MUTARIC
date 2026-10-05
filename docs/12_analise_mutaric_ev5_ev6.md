# 12 — Análise das auditorias externas "MUTARIC ev 5" e "MUTARIC ev 6" (ciclo 9)

> Documentos analisados: `MUTARIC ev 5.md` (rodada confirmatória do E10e com
> 200 sementes) e `MUTARIC ev 6.md` (estatística da comparação λ = 0,003 ×
> λ = 1), mais o zip `MUTARIC_E10e_200_SEMENTES.zip` — anexos externos
> recebidos em 04/10/2026. O zip contém **apenas saídas**
> (`e10e_200_resultados.json`, `e10e_200_pareto.csv`,
> `e10e_200_curva_pareto.png`) — **sem código**. A regra de aceitação é a
> mesma das auditorias anteriores: **nada aqui é aceito sem reprodução
> numérica**. Sem código, os números deles passam por checagem aritmética
> interna (marcada como tal) e por uma **replicação nossa, executada neste
> terminal**, que testa as alegações — nunca é confundida com a reprodução
> dos números deles. Estado deste ciclo: **36 testes, 12 figuras,
> E1–E10 + E10b + E10d + E10e_repl**, docs/00–docs/12.

## 1. O que os documentos trouxeram

1. **ev 5 — E10e confirmatório (200 sementes).** A rodada exploratória do
   E10e (24 sementes, `docs/11` §3 nº 20–23) virou teste confirmatório:
   mesma configuração, **200 sementes nunca vistas** (70000–70199), 240
   passos, λ ∈ {0, 0,001, 0,003, 0,01, 0,03, 0,1, 0,3, 1}, dois atacantes
   neurais, estado recorrente de 24 bits, métrica de privacidade
   `P = 1 − 2·max(0, A_máx − 0,5)`. Achados que o documento declara:
   a fronteira **ID foi estável** ({0,3; 1}), a fronteira **OOD não foi**
   ({0,1; 1} → {0,003}, com "o resultado anterior … **não foi
   reproduzido**"), λ = 1 é o melhor score ID e o pior praticamente em
   tudo fora, e "o efeito adversarial não é monotônico em λ". Recomendação
   nova: **λ = 0,003**. O documento mantém uma seção honesta "Ainda não
   demonstrado": acurácia neural ≤ 50% só mostra
   `A_neural,testado ≤ 0,5`, não `I(H;S) = 0`.
2. **ev 6 — estatística da comparação λ = 0,003 × λ = 1.** Como a rodada
   agregada **não guardou os scores por semente**, usou teste **t de Welch**
   a partir de médias e desvios (mais conservador que o pareado) e uma
   análise de **sensibilidade** por diferença de proporções
   (200 × 120 × 6 = 144000 previsões), advertindo em seguida que essas
   previsões **não são independentes** e que o teste adequado seria pareado
   por semente — o que exige acurácias por semente "que a rodada anterior
   não preservou". Veredito: **sem diferença detectável de utilidade**
   (ID p = 0,6559; OOD p = 0,9467), **maior reconstrução OOD de λ = 1**
   (z = 3,7790, p = 0,000157, como sensibilidade) → recomendação mantida
   em λ = 0,003.
3. **zip — só saídas.** JSON com o protocolo completo (hiperparâmetros
   idênticos aos da rodada exploratória, `n_test = 200`,
   `test_seed_start = 70000`), CSV com as mesmas 16 linhas e a coluna
   `pareto`, e a figura da curva. **Nenhum arquivo de código.**

## 2. Prova (regra do projeto)

O que foi feito, nesta máquina, em 04/10/2026:

1. **Checagem aritmética completa** — script externo `verifica_ev56.py`:
   **286/286 verificações OK**, distribuídas em: **80** tabelas do ev 5
   (documento × JSON: score, desvio, atacante neural, privacidade — 16
   linhas × 5 checagens); **96** CSV × JSON (16 linhas × 6 campos);
   **64** fórmulas (`P = 1 − 2·max(0, A−0,5)`, vantagem,
   `A_máx = max(execuções)`, `P = 1 ⇔ A ≤ 0,5`); **11** fronteiras de
   Pareto recalculadas por não-dominação + as 7 dominações de λ = 0,003
   sobre os demais pontos OOD; **8** afirmações numéricas do próprio ev 5
   (vantagens 0,23 e 0,62 p.p., 200 sementes, 240 passos, 8 λ, 24 bits);
   **16** estatísticas do ev 6 recalculadas com `scipy` a partir das
   médias/desvios deles (Welch: t, gl, p, IC e d de Cohen, nos dois
   splits); **7** da sensibilidade (144000, z e p ID/OOD, ΔA ID/OOD);
   **4** exploratório × confirmatório (fronteiras e λ = 0,1 dominado).
2. **Replicação executada aqui** — `experimentos.py::e10e_repl()`
   (chave `E10e_repl` do `resultados.json`): implementação **nossa** do
   protocolo descrito (ev 3/4 §1–4 + configuração do ev 5) sobre o ambiente
   E10b/E10d **já verificado** (o port do E10d regera o JSON externo
   exato), rodada **neste terminal com as mesmas 200 sementes do ev 5**
   (70000–70199): **163,6 s**, determinística, coberta por
   `test_e10e_repl_reproduz_as_publicacoes_desta_estacao` e
   `test_e10e_repl_determinismo_orcamento_e_formulas` (34 → **36 testes**),
   figura 12 `figs/e10e_repl.png`.
3. **Suíte completa** — **36/36 PASSOU**.

**Limites da prova:** sem código não há o que executar deles — os números
do ev 5/ev 6 são **consistentes internamente em 286 pontos**, mas não
reproduzidos por execução. A replicação do §4 **não é** reprodução dos
números deles: é uma implementação independente (inicialização, otimizador
e ataques são escolhas nossas, declaradas no `protocolo` da chave) que
testa as **alegações**. Concordância de estrutura é evidência; divergência
de ponto exato não refuta — e vice-versa.

## 3. Vereditos, alegação por alegação

### ev 5 (sem código — checagem aritmética interna)

| # | alegação do documento | verificação | veredito |
|---|---|---|---|
| 1 | tabela ID (8 linhas: score, desvio, neural, P) | 40/40 campos batem com o JSON; CSV idêntico | **consistente internamente — não reproduzível (sem código)** |
| 2 | tabela OOD (8 linhas) | 40/40 + CSV ✓ | **consistente internamente** |
| 3 | `P = 1 − 2·max(0, A−0,5)` e vantagem nas 16 linhas | 64/64 fórmulas ✓ | **consistente internamente** |
| 4 | Pareto ID = {0,3; 1} | recálculo de não-dominação: {0,3; 1} ✓ | **consistente — e reproduz a fronteira exploratória (estabilidade ID confirmada pela própria rodada)** |
| 5 | Pareto OOD = {0,003} (único; domina utilidade e privacidade dos demais) | recálculo ✓ + 7/7 dominações diretas ✓ | **consistente internamente** |
| 6 | "λ = 0,1 como ponto conservador OOD **não foi reproduzido**" | λ = 0,1 está dominado por 0,003 (mesmo P = 1, score pior) ✓ | **consistente — e confirma a previsão do `docs/11` §6: qualquer E12/P2.7 precisa fixar λ antes e usar sementes nunca observadas** |
| 7 | vantagens: 0,23 p.p. (λ = 0,3) e 0,62 p.p. (λ = 1) ID | 0,002326 e 0,00616 ✓ | **consistente internamente** |
| 8 | 200 sementes novas 70000–70199, 240 passos, 8 λ, 24 bits | protocolo do JSON ✓ | **consistente internamente** |
| 9 | "o efeito adversarial não é monotônico em λ"; λ = 1 pior OOD em score, vazamento e variabilidade | padrão das tabelas ✓ | **consistente internamente** |
| 10 | "A_neural ≤ 0,5 ≠ I(H;S) = 0" (seção "Ainda não demonstrado") | formulação correta, alinhada aos nossos padrões desde `docs/06` §8 | **aceita** |
| 11 | recomendação λ = 0,003 | coerente com as próprias tabelas | **aceita como recomendação operacional deles — não como fato estabelecido** (a anterior, λ = 0,1, morreu na própria rodada confirmatória) |
| 12 | protocolo de 7 pontos do ev 3/4 §9 (que sustenta a nossa P1.11) | cumpriram: sementes novas ✓, ≥ 200 ✓; **não cumpriram**: λ fixado antes ✗ (grade inteira inspecionada no teste), ICs ✗, dado por semente ✗, atacante temporal ✗ | **parcialmente cumprido — registrado como pendência (§8)** |

### ev 6 (sem código — estatística recalculada por nós com `scipy`)

| # | alegação do documento | verificação | veredito |
|---|---|---|---|
| 13 | Welch ID: ΔJ = +1,4380×10⁻⁵, t = 0,4459, gl ≈ 397,47, p = 0,6559, `IC = [−4,9022×10⁻⁵, 7,7783×10⁻⁵]`, d = 0,0446 | 8/8 recalculados exatos a partir das médias/desvios do ev 5 (n = 200) | **reproduzido por recálculo** |
| 14 | Welch OOD: ΔJ = −3,0627×10⁻⁶, t = −0,06685, gl ≈ 397,70, p = 0,9467, `IC = [−9,3135×10⁻⁵, 8,7009×10⁻⁵]`, d = −0,00668 | 8/8 ✓ | **reproduzido por recálculo** |
| 15 | ΔA ID = 0,003069 (0,307 p.p.); ΔA OOD = 0,007042 (0,704 p.p.) | 0,506160 − 0,503090 e 0,506660 − 0,499618 ✓ (no ID a exibição arredondada deles dá 0,003070; a conta em precisão cheia dá 0,003069 — arredondamento de exibição, sem efeito no veredito) | **reproduzido por recálculo** |
| 16 | sensibilidade: 144000 = 200 × 120 × 6; ID z = 1,6473, p = 0,0995; OOD z = 3,7790, p = 0,000157 | 5/5 ✓ (z e p com teste normal exato) | **reproduzido por recálculo** |
| 17 | "as 144 mil previsões não são independentes … o teste de proporções tem amostra efetiva artificialmente grande" | é exatamente a nossa **P1.9 — pseudorreplicação**, levantada na primeira auditoria | **confirmada pela própria auditoria** |
| 18 | "o teste adequado é pareado por semente … a rodada anterior não preservou" | limitação declarada corretamente; nós salvamos por semente (§4) | **aceita como limitação — e suprida na nossa replicação** |
| 19 | conclusão: sem diferença de utilidade; λ = 0,003 domina sob critério conservador | coerente com as próprias estatísticas; o pareado do §4 tem mais poder e acha diferença pequena (§4 g) | **consistente internamente; a conclusão "utilidade indistinguível" fica marcada como dependente do teste usado** |

## 4. Nossa replicação (E10e_repl) — o que apareceu ao rodar aqui

Comando: `e10e_repl()` — 200 sementes do ev 5, 8 λ, ambiente E10b/E10d
verificado, **163,6 s** neste terminal. Tabelas completas na §7; resumo:

| alegação do ev 5/6 | nossa réplica | veredito |
|---|---|---|
| λ = 1 é o melhor score ID | −0,00362529 vs demais ∈ [−0,00362996; −0,00362811] | **confirmada** |
| λ = 1 é o pior em privacidade ID | P = 0,99138 vs demais ∈ [0,99836; 0,99939] | **confirmada** |
| λ = 1 é o pior em score **e** privacidade OOD | score −0,00529254 (o pior) e P = 0,98649 (o pior) | **confirmada** |
| efeito não monotônico em λ | P ID oscila (0,99836 … 0,99939 … 0,99138) | **confirmada** |
| Pareto ID = {0,3; 1} | nosso {0,1; 0,3; 1} — **contém** os dois pontos deles | **confirmada em conteúdo, ampliada em forma** (nosso λ = 0,1 extra não é dominado aqui) |
| Pareto OOD = {0,003} | nosso {0,01} — **não é o mesmo ponto** | **estrutura confirmada, ponto não**: nos dois casos o dominador é um λ pequeno sobre a prateleira P = 1; λ = 1 é pior nos dois eixos |
| ev 6: λ = 1 vaza mais OOD (z = 3,7790) | ΔA pareado = +0,006153, `IC = [0,00460, 0,00767]` > 0 | **confirmada com o método pareado que eles pediram** |
| ev 6: sem diferença detectável de utilidade | pareado ID ΔJ = +4,38×10⁻⁶, `IC = [1,74×10⁻⁶, 6,99×10⁻⁶]` (fora de 0); OOD ΔJ = −1,20×10⁻⁵, `IC = [−1,65×10⁻⁵; −7,61×10⁻⁶]` (fora de 0) | **não confirmada como "indistinguível"** — com pareado as diferenças são detectáveis (ID favorável a λ = 1, OOD favorável a 0,003), embora minúsculas; a direção das médias deles (ID +, OOD −) é a mesma |

**O teste que eles não pôde fazer.** O ev 6 §5 diz: "será necessário
salvar a acurácia do atacante separadamente em cada semente, o que a
rodada anterior não preservou". A replicação salva **score por semente**
(200) e **acurácia por semente do atacante neural** (100 — a metade de
teste) para λ = 0,003 e λ = 1, e roda o bootstrap pareado com IC — o
protocolo exato que eles recomendaram. Os quatro ICs saem estritamente
afastados de zero: **um** a favor de λ = 1 (utilidade ID) e **três** a
favor de 0,003 (utilidade OOD e privacidade nos dois splits).

**Ressalva permanente:** isto é **nossa implementação** do protocolo
descrito. Não tendo o código deles, não é possível saber onde as
implementações divergem (inicialização, rolagem do estado durante o
treino, número real de atualizações dos atacantes). A replicação
**sustenta as direções centrais** (λ = 1 vaza mais; λ pequeno é a escolha
OOD; utilidade quase igual) e **não sustenta o ponto exato** do Pareto
OOD deles. Nada aqui é citado como número deles.

## 5. O que foi adotado

| adotado | onde |
|---|---|
| **`e10e_repl()`** — replicação do protocolo Pareto (ev 5/6) com 200 sementes, pareado por semente, determinística, roda no `run_all` e na CI | `experimentos.py::e10e_repl()`, chave `E10e_repl` do `resultados.json` |
| **figura 12** — Pareto ID/OOD nossa × deles e os quatro ICs pareados | `figs/e10e_repl.png` |
| **2 testes novos (34 → 36)** — regressão das tabelas e vereditos da réplica + determinismo/24 bits/fórmula de P/Pareto/disjunção de sementes | `tests/test_smoke.py` |
| **salvar score E acurácia do atacante POR SEMENTE** como disciplina — é o dado que faltou no ev 6 para o teste correto; já fazemos assim desde o E10b e agora fica registrado como exigência explícita | `E10e_repl.pareado_l1_vs_l003`, `docs/04` (lição ev 5/6) |
| **comparação estatística: pareado por semente > Welch pela média/desvio** — mais poder para a mesma amostra; a conclusão "utilidade indistinguível" deles é dependente do teste usado | `docs/12` §3 nº 19, `docs/04` |
| **"a fronteira OOD não é estável entre rodadas"** — a própria auditoria abandonou λ = 0,1; reforço da regra de fixar λ **antes** do teste (P3.4) e de usar sementes nunca vistas | `docs/04` P3.4, `docs/11` §6 |
| **lição da pseudorreplicação confirmada pelo autor** (ev 6 §5 = nossa P1.9) — a advertência deles sobre as 144000 previsões vira justificativa registrada do protocolo hierárquico | `docs/04` P1.9 |
| **epistêmica de "A_neural ≤ 0,5 ≠ I(H;S) = 0"** — formulação adotada como padrão de redação dos nossos resultados de ataque | `docs/12` §3 nº 10, READMEs |
| **resultado não confirmado publicado** — o Pareto OOD exato deles não se repetiu na réplica, e isto é publicado com a mesma proeminência do que confirmou | `README.md`, `README.en.md` |

## 6. Ressalvas mantidas (o que NÃO foi adotado sem prova)

- **Números do ev 5/ev 6: consistentes, não executáveis.** Sem código no
  zip, nenhum valor deles é "reproduzido por execução" — só verificado
  aritmeticamente (286 pontos). O status deles no inventário é o mesmo do
  E10c/E10e do ciclo 8, com a diferença de que agora há um JSON/CSV deles
  para cruzar.
- **A replicação não substitui a reprodução.** `E10e_repl` **não** regera
  os números do ev 5 (nem poderia): ela testa alegações. Os números
  publicados como "deles" continuam sendo apenas os das tabelas do
  documento, com a marcação de origem.
- **λ = 0,003 como "escolha certa": não.** É a recomendação operacional
  da rodada deles; a rodada anterior recomendava λ = 0,1 e morreu nela.
  Adotamos a **lição** (fixar antes, testar em sementes novas), não o
  valor.
- **"Utilidade indistinguível" (ev 6):** válida para o teste usado (Welch
  sobre médias/desvios). Nosso pareado acha diferença pequena mas fora de
  zero — ambos os fatos ficam publicados; nenhum dos lados é apresentado
  como definitivo.
- **Atacante temporal: ninguém rodou.** O ponto 7 do protocolo §9 do ev
  3/4 continua em aberto do lado deles e do nosso — a P1.11 permanece.
- **graus de liberdade da nossa réplica:** inicialização a partir do
  `_e10b_train`, rolagem do estado no treino, `int` no ridge (sem o bug
  uint8 do `e10d.py`), dois atacantes neurais de 64 unidades com
  `neural_attack_epochs = 10` — tudo declarado na chave `protocolo` e
  documentado aqui; qualquer leitor deve tratar a réplica como **nossa**.

## 7. Números reproduzidos (`E10e_repl`, esta terminal, 200 sementes)

**ID — score × atacante neural × privacidade (200 sementes):**

| λ | score médio | atacante neural | P |
|---|---|---|---|
| 0 | −0,00362969 | 0,50078 | 0,99844 |
| 0,001 | −0,00362971 | 0,50079 | 0,99843 |
| 0,003 | −0,00362967 | 0,50082 | 0,99836 |
| 0,01 | −0,00362994 | 0,50079 | 0,99842 |
| 0,03 | −0,00362996 | 0,50044 | 0,99911 |
| 0,1 | **−0,00362931** | 0,50031 | **0,99939** |
| 0,3 | −0,00362811 | 0,50060 | 0,99879 |
| 1 | **−0,00362529** | **0,50431** | **0,99138** |

Pareto ID nosso: **{0,1; 0,3; 1}** — contém o deles {0,3; 1}.

**OOD — score × atacante neural × privacidade (mesmas 200 sementes):**

| λ | score médio | atacante neural | P |
|---|---|---|---|
| 0 | −0,00528062 | 0,49840 | 1,00000 |
| 0,001 | −0,00528059 | 0,49838 | 1,00000 |
| 0,003 | −0,00528054 | 0,49839 | 1,00000 |
| 0,01 | **−0,00528048** | 0,49847 | 1,00000 |
| 0,03 | −0,00528050 | 0,49840 | 1,00000 |
| 0,1 | −0,00528200 | 0,49886 | 1,00000 |
| 0,3 | −0,00528172 | 0,49923 | 1,00000 |
| 1 | **−0,00529254** | **0,50676** | **0,98649** |

Pareto OOD nosso: **{0,01}** (deles: {0,003}) — mesma prateleira
P = 1, ponto exato diferente.

**Teste pareado por semente, λ = 1 − λ = 0,003 (o que o ev 6 não pôde
fazer):**

| regime | medida | Δ | IC95% | vitórias | n |
|---|---|---|---|---|---|
| ID | utilidade (score) | **+4,3759×10⁻⁶** | [1,7386×10⁻⁶; 6,9921×10⁻⁶] | 62,0% | 200 |
| ID | atacante neural | **+0,0025833** | [0,0011528; 0,0040486] | 60,0% | 100 |
| OOD | utilidade (score) | **−1,2002×10⁻⁵** | [−1,6540×10⁻⁵; −7,6114×10⁻⁶] | 39,5% | 200 |
| OOD | atacante neural | **+0,0061528** | [0,0046042; 0,0076736] | 77,0% | 100 |

Todos os quatro ICs estão estritamente afastados de zero: utilidade ligeiramente
melhor para λ = 1 ID, pior para λ = 1 OOD; reconstrução significativamente
maior para λ = 1 **nos dois splits** (mesma direção do z do ev 6).

**Números externos reproduzidos por recálculo (ev 6, via `scipy`):**
Welch ID t = 0,4459 / gl = 397,47 / p = 0,6559 / IC [−4,9022×10⁻⁵;
7,7783×10⁻⁵] / d = 0,0446; Welch OOD t = −0,06685 / gl = 397,70 /
p = 0,9467 / IC [−9,3135×10⁻⁵; 8,7009×10⁻⁵] / d = −0,00668; z ID =
1,6473 / p = 0,0995; z OOD = 3,7790 / p = 0,000157.

## 8. Pendências geradas por este ciclo

| pendência | motivo | onde |
|---|---|---|
| **P1.11 mantida e afinada** — o protocolo §9 do ev 3/4 continua sem o atacante **temporal** e sem λ fixado antes do teste; a nossa versão deve usar exatamente o pareado por semente demonstrado aqui (score + acurácia do atacante por semente, bootstrap pareado) | ev 5/6 cumpriram só 2 dos 7 pontos (§3 nº 12) | `docs/04` |
| **P3.4 reforçada** — "fixar λ antes e nunca inspecionar a grade no teste": a própria auditoria perdeu a fronteira OOD entre rodadas | §3 nº 6 | `docs/04` |
| **P1.9 ganha o selo do autor** — a pseudorreplicação levantada na 1ª auditoria foi reconhecida pelo próprio ev 6 §5 | §3 nº 17 | `docs/04` |
| **P2.7 com o caminho já trilhado** — a rota adversarial (E10d/E10e) é a que a auditoria usou e a que a nossa deve seguir direto; a nulidade linear continua publicada | `docs/11` §8, mantida | `docs/04` |
| **P1.10 e P2.6** seguem abertas como nos ciclos anteriores — nada de novo as fecha | — | `docs/04` |
| **PRÓXIMO CICLO** — se vier código do E10e/ev5, executar e cruzar com o JSON deles (a regra inteira deste ciclo vira reprodução de verdade) | zip sem código | `docs/07` |

## Summary (EN)

The fifth external verification package brings the **confirmatory round of E10e**
(`MUTARIC ev 5`, 200 new seeds 70000–70199, same configuration, privacy
metric `P = 1 − 2·max(0, A−0,5)`) and the **statistics** of the
λ = 0,003 × λ = 1 comparison (`MUTARIC ev 6`), plus a zip with **outputs
only — no code**. Verification here: **286/286** arithmetic checks
(document × JSON × CSV, privacy formulas, Pareto frontiers recomputed,
Welch t-tests and proportion z-tests recomputed with `scipy` from their
summary statistics) and a **replication of the protocol executed on this
terminal** (`E10e_repl`, 163.6 s, same 200 seeds, our implementation on
the verified E10b/E10d environment, covered by 2 new tests → **36 tests,
12 figures**). Verdicts: ev 5 is internally consistent — the ID frontier
{0.3; 1} was stable, the OOD frontier was **not** ({0.1; 1} → {0.003}),
confirming the caution we published in `docs/11` §6; ev 6's statistics are
fully reproducible from ev 5's means/SDs, and its own independence warning
is exactly our P1.9 (pseudoreplication). Our replication **confirms the
directions** (λ = 1: best ID score, worst privacy everywhere, largest OOD
leakage — with the paired per-seed bootstrap ev 6 could not run) and
**does not reproduce the exact OOD Pareto point** ({0.01} vs {0.003}),
which is published with the same prominence. Adopted: per-seed scores and
per-seed attacker accuracies as standing discipline, paired > Welch for
this sample size, "fix λ before the test", and the epistemic phrasing
"A_neural ≤ 0.5 ≠ I(H;S) = 0". Open: P1.11 (temporal attacker still
nobody ran), P3.4, P2.7, P1.10.
