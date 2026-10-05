# 10 — Análise da auditoria externa "MUTARIC ev 2" (ciclo 7)

> Documento analisado: `MUTARIC ev 2.md` + código `e10b.py` + `README.md`
> (anexo externo recebido em 04/10/2026, pasta `mutaric b/MUTARIC_E10b/`).
> A mesma regra de aceitação do MutaCore vale para quem nos audita:
> **nada aqui é aceito sem reprodução numérica**. O `e10b.py` deles foi
> executado nesta máquina e o port `E10b_controles()` regera o resultado
> externo **idêntico** (§2). Estado resultante deste ciclo: **32 testes,
> 10 figuras, E1–E10 + E10b**, docs/00–docs/10.

---

## 1. O que o documento trouxe

1. **Um "E10" próprio** — uma re-implementação da ideia de orçamento igual,
   mas com **24 bits quantizados por memória** (6 canais × 4 bits), alvo
   escalar `S* = 0,72` e `score = −(perda + 0,08·esforço)`. Nesse ambiente,
   o resíduo vence a memória assinada (`Δ_ID = +0,0006104`,
   `IC95% = [0,0005636, 0,0006594]`; `Δ_OOD = +0,0008347`,
   `[0,0007763, 0,0008938]`; `P(Δ>0)=1` nas 120 sementes).
2. **A autocrítica correta**: esse comparador é uma EMA *assinada* num
   ambiente de perturbações de média nula e variância persistente — ela sofre
   cancelamento, enquanto `|Δ|` e `Δ²` conservam volatilidade. Logo, o
   resultado "não demonstra que o resíduo supera toda memória de igual
   capacidade" — só que *a estatística residual adequada supera uma memória
   assinada genérica*.
3. **O experimento E10b**: o resíduo quadrático (`square_ema`) contra **cinco
   controles fortes de igual orçamento** — sem memória, EMA assinada, EMA de
   magnitude, janela curta (24 bits exatos em um inteiro) e estado recorrente
   aprendido — com 200 sementes pareadas, IC bootstrap 95%, teste OOD que
   altera duração + frequência + intensidade, e separação estrita de sementes
   de treino (100000+) e de avaliação (50000+).
4. **O veredito do E10b**: a formulação forte
   `resíduo > memória convencional de igual capacidade` **não é sustentada
   nesse ambiente** — o resíduo perde para a EMA de magnitude e para o
   recorrente aprendido nos dois splits, e só vence a janela curta dentro da
   distribuição. O melhor agente é o recorrente aprendido.
5. **Uma nova direção (E10c)**: resíduo preditivo comprimido sob restrição
   explícita de não reconstrução (`I(R;sign(Δ)) ≈ 0`,
   `I(R;custo futuro) > 0`, `J(R) > J(M)` contra memórias fortes).

## 2. Prova de reprodução (regra do projeto)

O que foi feito, nesta máquina, em 04/10/2026:

1. **Execução do `e10b.py` externo** — `EXIT=0`, 108 s, gerou
   `e10b_resultados.json`. Comparação campo a campo com as tabelas publicadas
   no documento: **58/58 verificações OK** (24 números de tabela ID/OOD,
   24 campos de comparações pareadas — Δ, IC, vitórias —, 8 taxas de
   decodificação e os 2 vencedores), com diferença exatamente 0 em todos.
2. **Port para o nosso código** — `experimentos.py::e10b_controles()`
   (chave `E10b_controles` do `resultados/resultados.json`) foi comparado ao
   `e10b_resultados.json` externo com igualdade estrita: **idêntico em
   estrutura e valores** (106 s por execução).
3. **Cobertura permanente** — `test_e10b_reproduz_o_documento_mutaric_ev2`
   regressa as tabelas publicadas; `test_e10b_orcamento_determinismo_e_separacao`
   cobre o orçamento de 24 bits, o quantizador Q4, a
   determinismo por semente e a disjunção treino/avaliação.

Números reproduzidos ⇒ alegações abaixo marcadas **confirmada** valem
tanto para o documento quanto para o nosso port.

## 3. Vereditos, alegação por alegação

| # | alegação do documento | verificação | veredito |
|---|---|---|---|
| 1 | tabelas ID/OOD do E10b (6 memórias × score e perda) | execução do `e10b.py` + comparação: 24/24 idênticos | **confirmada** |
| 2 | Δ pareados com IC95% bootstrap e % de vitórias por semente | 6 comparações × 4 campos = 24/24 idênticos | **confirmada** |
| 3 | melhor agente = recorrente aprendido nos dois splits | reproduzido (`melhor_score = learned_recurrent`) | **confirmada** |
| 4 | nenhuma memória recupera o sinal apagado (decodificador 0,4985–0,5018) | reproduzido (8/8 taxas) | **confirmada** |
| 5 | "o E10b refuta a formulação forte **neste ambiente**" | ICs desfavoráveis ao resíduo contra magnitude e recorrente nos **dois** splits (margens de 10⁻⁵ a 10⁻⁴, bem fora de zero) | **confirmada — aceita com o escopo declarado (ambiente deles)** |
| 6 | mecanismo: em ambiente de variância com média nula, memória assinada cancela e `|Δ|`/`Δ²` conservam volatilidade | análise correta e coerente com os próprios números (EMA assinada é a pior de todas as memórias: ID −0,003677) | **aceita** |
| 7 | "baixa reconstrução do conteúdo não é propriedade exclusiva do resíduo" | 4 memórias deles ≈ 0,5; no **nosso** E10: AR reconstrói quase no piso sem memória (RMSE 0,1018 vs A0 0,1083) — coerente | **confirmada/consistente** |
| 8 | E10 (parte 1): resíduo vence assinada nas 120 sementes (`Δ_ID=0,0006104`, `Δ_OOD=0,0008347`, `P=1`) | `e10.py` **não foi fornecido** — não há o que executar | **não verificável** |
| 9 | "três testes novos" (E10) e "quatro testes" (E10b) | arquivos de teste **não fornecidos** | **não verificável** |
| 10 | o recorrente aprendido tem "orçamento de 24 bits" | os pesos `13×6 = 78` parâmetros estão fora do orçamento; o próprio código deles o declara como "parâmetros fixos da política" | **aceito com ressalva**: a comparação é *estado mutável igual, parâmetros livres* |
| 11 | o documento descreve "o E10" como se fosse o do repositório | **não é o mesmo experimento**: o nosso E10 usa 6 float64 por agente, episódios do `mundo`, alvo vetorial `S*` e `J = −dist + 0,5·acerto`; o deles usa 24 bits quantizados, `S* = 0,72` e `score = −(perda + 0,08·esforço)` | **números não confrontam o nosso JSON** — a crítica *conceitual* transfere e foi adotada (§5) |

## 4. O que o E10b refuta — e o que ele NÃO refuta

**Refuta (no ambiente deles):** a formulação forte
"resíduo quadrático > memória convencional de igual capacidade". O resíduo
perde para a EMA de magnitude (ID `−0,0001272`, OOD `−0,0000237`) e para o
recorrente aprendido (ID `−0,0001904`, OOD `−0,0003150`) com ICs que não
tocam zero, e vence só a janela curta no ID (`+0,0000370`).

**NÃO refuta:**

1. as **3 condições do nosso E10** (`docs/09` §5) — elas seguem verdadeiras
   *no nosso ambiente* e estão regredidas; nenhum número publicado mudou;
2. os resultados mecanísticos E5–E9 nem a análise do MutaCore;
3. a utilidade do resíduo como estatística de 2ª ordem — o próprio E10b
   mostra que ela *serve* (todas as memórias de magnitude vencem a
   assinada e a sem memória).

**O que ele expõe do nosso E10:** o comparador AM (EMA do conteúdo) também
não é a estatística suficiente para distúrbios de magnitude — a vitória do
AR sobre o AM pode pertencer à *escolha da estatística* (segunda ordem), não
a uma categoria nova de "resíduo". Isso é exatamente a nossa ressalva
`AR ≈ A0` (`docs/09` §5.2 e §7.4), agora demonstrada de forma independente
por um experimento alheio. **Adotado** como limitação escrita
(`docs/09` §7.6) e como pendência P1.10 (§5).

## 5. O que foi adotado

| o que | onde ficou |
|---|---|
| **E10b portado para o nosso código** — port fiel, determinístico (tudo semeado), roda no `run_all` e na CI | `experimentos.py::e10b_controles()`, chave `E10b_controles` do `resultados.json` |
| **figura 10** — scores ID/OOD e Δ pareados com IC | `figs/e10b_controles.png` |
| **2 testes novos (30 → 32)** — regressão das tabelas publicadas + orçamento/determinismo/separação de sementes | `tests/test_smoke.py` |
| **limitação do comparador** escrita no E10 | `docs/09` §7.6 |
| **P1.10** — controles fortes + OOD + IC bootstrap pareado **no nosso ambiente do E10** (mundo, `S*` vetorial, J) | `docs/04` |
| **P2.7** — E10c: resíduo preditivo comprimido com restrição de não reconstrução | `docs/04` |
| **metodologia passou a padrão**: IC bootstrap pareado sobre diferenças por semente, OOD que altera duração+frequência+intensidade, treino/avaliação em sementes disjuntas | `docs/04` P1.10, `docs/10` §2 |
| **resultado negativo publicado com a mesma proeminência** do positivo (seção própria no README, veredito no `resultados.json`) | `README.md`, `README.en.md` |

## 6. Ressalvas mantidas (o que NÃO foi adotado sem prova)

1. **Parte 1 do documento (E10 deles) fica como não verificável** — sem
   `e10.py` e sem os testes deles, os números `0,0006104/0,0008347` não
   entram em nenhum doc como fato, apenas como "alegação não reproduzível
   com o material fornecido".
2. **78 pesos do recorrente fora dos 24 bits** — aceito porque está declarado
   no código deles, mas a leitura correta é "estado mutável igual, parâmetros
   livres"; qualquer citação deve manter essa ressalva.
3. **Peso 0,08 do esforço no score** é um grau de liberdade do pesquisador
   (não há análise de sensibilidade no documento). A *direção* do ranking ID
   depende dele (o resíduo tem menor perda mas mais esforço que a magnitude,
   e perde no score por isso) — mesmo com outro peso o resíduo não passaria
   a vencer o recorrente, mas o tamanho dos Δ é sensível.
4. **Decodificador simples** (limiar por canal): "≈ acaso" vale para *esse*
   decodificador — o documento declara isso ("pelo decodificador testado").
   **Atualização do ciclo 8** (`docs/11` §4): a auditoria ev 3/4 mostrou que
   os ataques *lineares* do E10d eram **degenerados** (uint8 em `2*Y−1`, alvos
   `{255,1}`) e mesmo assim um atacante neural achou 55,6% de reconstrução —
   ou seja, "testes lineares ≈ acaso" pode significar "o teste não testa
   nada". A ressalva aqui permanece (os números de cima vêm do limiar) e a
   pergunta "um atacante neural/temporal acha o que o limiar não acha?" virou
   a pendência **P1.11**.
5. **Ambiente deles é sintético e construído** (hot-spots de variância);
   a refutação é correta *dentro* desse ambiente e não se auto-generaliza —
   como também o nosso E10 vale no nosso. A ponte entre os dois ambientes é
   o objeto de **P1.10**.
6. **E10c/E10b não substituem o E11** já definido em `docs/09` §8 (E10 com
   política aprendida): são caminhos distintos registrados na fila.

## 7. Números reproduzidos (`E10b_controles`, 200 sementes pareadas)

Score médio (maior = melhor) e perda homeostática — todos os valores
reproduzidos com diferença 0:

| memória | score ID | perda ID | score OOD | perda OOD |
|---|---|---|---|---|
| sem memória | −0,004586 | 0,004265 | −0,007148 | 0,006827 |
| EMA assinada | −0,003677 | 0,003256 | −0,005743 | 0,005308 |
| EMA de magnitude | −0,003541 | 0,002971 | −0,005463 | 0,004893 |
| **resíduo quadrático** | −0,003668 | 0,002828 | −0,005487 | 0,004809 |
| janela curta | −0,003705 | 0,002448 | −0,005328 | 0,004045 |
| **recorrente aprendido** | **−0,003478** | 0,002442 | **−0,005172** | 0,003941 |

Comparações pareadas `Δ = resíduo − controle` (IC95% bootstrap, vitórias por
semente):

| split | controle | Δ | IC95% | vitórias | veredito |
|---|---|---|---|---|---|
| ID | magnitude | −0,0001272 | [−0,0001370, −0,0001171] | 5,5% | desfavorável |
| ID | janela curta | **+0,0000370** | [+0,0000222, +0,0000517] | 71% | favorável |
| ID | recorrente | −0,0001904 | [−0,0002046, −0,0001762] | 2% | desfavorável |
| OOD | magnitude | −0,0000237 | [−0,0000332, −0,0000142] | 32,5% | desfavorável |
| OOD | janela curta | −0,0001596 | [−0,0001930, −0,0001272] | 26,5% | desfavorável |
| OOD | recorrente | −0,0003150 | [−0,0003521, −0,0002812] | 4% | desfavorável |

Decodificação do sinal apagado (acaso = 0,5): magnitude 0,5017/0,4991,
resíduo 0,5018/0,4989, janela 0,4997/0,4985, recorrente 0,5012/0,4990
(ID/OOD) — nenhuma memória recupera o conteúdo.

**Veredito publicado:** no ambiente do E10b, contra memórias fortes de igual
orçamento (24 bits), **o resíduo quadrático não vence** — vence apenas a
assinada e a sem memória. O benefício pertence à estatística de segunda
ordem e à capacidade de aprender dependências temporais, não a uma categoria
nova de "resíduo". Isso é coerente com a nossa ressalva `AR ≈ A0` do E10
próprio: **o resíduo supera a memória convencional fraca, não a ausência de
memória nem as memórias fortes.**

## 8. Pendências geradas por este ciclo

- **P1.10** — repetir o E10b (controles fortes, OOD, IC bootstrap pareado)
  **no nosso ambiente do E10** — `mundo`, `S*` vetorial, `J` — para decidir
  se a vitória `J(AR) > J(AM)` sobrevive a comparadores fortes aqui também
  (`docs/04`).
- **P2.7** — E10c: resíduo preditivo comprimido sob restrição de não
  reconstrução (`docs/04`). Candidato natural a E12, mantido o E11
  (política aprendida) definido em `docs/09` §8.

> **Continuação (ciclo 8, `docs/11`):** a terceira auditoria (ev 3/4)
> executou a versão **linear** dessa mesma ideia (E10c externo) e o efeito
> sobre o score foi **nulo** (ICs contêm zero; λ alto ainda elevou o
> vazamento) — daí a atualização do P2.7 para penalidade **adversarial**
> (`docs/04`). Da auditoria saíram também **P1.11** (atacante neural e
> temporal contra os nossos estados) e o E10d portado (`docs/11`).

---

## Summary (EN)

A second external audit ("MUTARIC ev 2") was verified by execution: its
`e10b.py` was run on this machine (108 s, exit 0) and **58/58 published
numbers reproduce exactly** (ID/OOD tables, paired deltas with 95% bootstrap
CIs, per-seed win rates, signal-decoder rates, winners). The code was ported
to `experimentos.py::e10b_controles()` as a seeded, deterministic experiment
(key `E10b_controles`, figure `e10b_controles.png`, tests 30 → 32); the port
regenerates the external JSON identically. The audit's own "E10" (24-bit
quantized memories, scalar target, score penalizing effort) is **not** the
same experiment as our published E10 (6 float64, world episodes, vector
target, J = −dist + 0.5·accuracy): its numbers do not confront our JSON, but
its conceptual critique transfers and was adopted as a written limitation
(`docs/09` §7.6). Its first part (`e10.py`, test files) was **not provided
and is unverifiable**. **Verdict of the reproduced experiment (E10b): the
strong formulation is refuted in that environment** — the quadratic residue
loses to magnitude EMA and to the learned recurrent state in both splits
(all CIs exclude zero) and beats only the short window in-distribution; the
best agent is the learned recurrent model, and no memory recovers the erased
signal above chance. This is consistent with our own E10 caveat (AR ≈ A0):
the residue beats a weak conventional memory, not the absence of memory nor
strong memories of equal capacity. Accepted with reservations: 78 recurrent
weights outside the 24-bit budget (declared: equal mutable state, free
parameters), an undeclared 0.08 effort weight in the score, and a synthetic
variance-hot-spot environment. New roadmap items: **P1.10** (strong
controls + OOD + paired bootstrap CI inside *our* E10 environment) and
**P2.7** (E10c predictive compressed residue under a non-reconstruction
constraint). Status: 32 tests, 10 figures, E1–E10 + E10b, docs/00–docs/10.
*Cycle-8 continuation:* the third audit (`docs/11`) independently implemented
the **linear** version of P2.7's idea (external E10c) and got a **null**
effect (CIs contain zero; high λ even increased leakage) — P2.7 is now
specified with an **adversarial** penalty; that cycle also added **P1.11**
(neural/temporal attackers against our own states) and ported E10d.
