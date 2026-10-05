# 11 — Análise da auditoria externa "MUTARIC ev 3 e 4" (ciclo 8)

> Documento analisado: `MUTARIC ev 3 e 4.md` + zip `MUTARIC_E10d.zip`
> (`e10d.py`, `resultados/e10d_resultados.json`, `tests/test_e10d.py`) —
> anexo externo recebido em 04/10/2026, pasta `IA-RESEARCH-MUTARIC-main/`.
> A mesma regra de aceitação das auditorias anteriores: **nada aqui é aceito
> sem reprodução numérica**. O `e10d.py` deles foi executado nesta máquina e
> regenerou o JSON publicado **idêntico** (§2); o port `E10d_controles()`
> regera os mesmos valores. E10c e E10e vieram **sem código** — para eles só
> há checagem aritmética interna, marcada como tal. Estado deste ciclo:
> **34 testes, 11 figuras, E1–E10 + E10b + E10d**, docs/00–docs/11.

---

## 1. O que o documento trouxe (três experimentos, uma sequência)

A auditoria ev 3/4 fecha uma cadeia hipótese → refutação → correção:

1. **E10c — penalidade linear de não reconstrução.** Sobre o resíduo
   preditivo (`h ← Q₄(Ah + Bs s + Bq q + b)`, 24 bits), treino por mínimos
   quadrados com penalidade de covariância
   `L = ‖XW−Y‖² + λ‖ZᵀXW‖² + ρ‖W‖²`, grade `λ ∈ {0, 0,1, 1, 10, 100, 1000}`
   selecionada só na validação (critério: atacante quadrático ≤ 0,505 e,
   entre os admissíveis, maior score) → **λ = 1**. Resultado: efeito sobre o
   score **inconclusivo** (ICs contêm zero nos dois splits), redução de
   vazamento desprezível em ID e **aumento** em OOD; λ alto *elevou* a
   acurácia do atacante quadrático. Conclusão do documento: a penalidade
   linear é quase redundante porque a recorrência já descartava quase todo o
   sinal — e `Cov(h,z) ≈ 0` **não** implica `I(h;z) = 0` (nome correto:
   "penalidade substituta de não reconstrução linear", não garantia de
   privacidade).
2. **E10d — jogo adversarial em arquitetura nova.** Codificador sigmoidal
   `h ← Q₄[σ(Wh h + Ws s + Wq q + b)]` com *straight-through estimator* e
   gradiente recorrente truncado em um passo; adversário interno MLP com
   inversão de gradiente; λ ∈ {0, 0,01, 0,03, 0,1, 0,3} selecionado na
   validação sob limite de reconstrução neural 0,515. **Nenhum λ atingiu o
   limite → o protocolo aplicou o fallback programado e escolheu o maior
   score (λ = 0,3)** — registrado pelo próprio documento como seleção por
   fallback, não como satisfação da restrição. Avaliação com atacante neural
   externo (48 unidades, inicialização própria, metade das trajetórias
   treina / metade testa) além dos ataques linear e quadrático.
3. **E10e — adversarial sobre o recorrente forte do E10b.** Copia `A`, `Bq`
   e `b` do E10b, adiciona bloco assinado `Bs = 0`, e faz a fronteira de
   Pareto `(J_λ, A_neural,λ)` para λ ∈ {0 … 1}. Execução **reduzida e
   exploratória** (24 sementes, 240 passos, λ inspecionados no conjunto de
   teste — limitação declarada pelo próprio documento), com recomendação de
   fixar λ = 0,1 antes de um teste confirmatório maior e pré-registrado.

Vereditos anunciados pelo documento: H1 (atacante neural acha vazamento que
os lineares não acham) **confirmada**; H2 (adversarial reduz reconstrução
neural) **parcial**; H3 (privacidade sem perda na mesma arquitetura)
**confirmada nesta execução**; H4 (adversarial supera controles fortes)
**refutada**.

## 2. Prova de reprodução (regra do projeto)

O que foi feito, nesta máquina, em 04/10/2026:

1. **Testes externos** — `python tests/test_e10d.py`: **3/3 PASSOU**
   (`test_budget_shape`, `test_quantized_deterministic`, `test_smoke`),
   `EXIT=0`.
2. **Execução do `e10d.py` externo** — `EXIT=0`, **170,6 s**, gerou
   `e10d_resultados.json`. Comparação campo a campo com o JSON publicado no
   zip: **idêntico — 0 diferenças em 129 números** (protocolo, varredura de
   validação, ID, OOD, efeitos adversariais e os 8 comparadores).
3. **Checagem das tabelas do documento** — script `verifica_ev34.py`:
   **113/113 verificações OK**, abrangendo (a) as tabelas E10d do documento ×
   o JSON regenerado — **78**: 10 da varredura, 24 de ID/OOD, 32 de
   comparadores, 7 de vitórias, 5 de fallback/H2; (b) a aritmética interna
   dos experimentos **sem código** — **30**: 9 do E10c (ΔJ, ICs, seleção de
   λ, elevação OOD, ΔJ × IC) e 21 do E10e (16 colunas `P = 1 − 2·V`, 2
   melhores scores, 2 fronteiras de Pareto recalcadas, 1 vantagem da λ=1);
   e (c) a prova do atacante linear degenerado (§4) — **5**.
4. **Port para o nosso código** — `experimentos.py::e10d_controles()`
   (chave `E10d_controles`) regera exatamente os mesmos valores externos
   (177,0 s por execução), coberto por
   `test_e10d_reproduz_o_documento_mutaric_ev3_ev4` e
   `test_e10d_determinismo_orcamento_e_separacao`.

**Limites da prova:** E10c e E10e **não têm código no anexo** — não há o
que executar; deles só passou checagem aritmética interna (Δ = Jpriv − J0,
IC contendo zero, critério de seleção de λ, `P = 1 − 2·V` e recálculo das
fronteiras de Pareto a partir das próprias tabelas). Alegações que dependem
de execução (24 sementes, 240 passos, ICs deles, comparações do E10c contra
os controles do E10b) ficam **não reproduzíveis** com o material fornecido.

## 3. Vereditos, alegação por alegação

### E10c (sem código — checagem aritmética interna)

| # | alegação do documento | verificação | veredito |
|---|---|---|---|
| 1 | ID: ΔJ = −2,99×10⁻⁸, `IC95% = [−2,06×10⁻⁷, 1,46×10⁻⁷]` → efeito inconclusivo | −0,0034777513 − (−0,0034777214) = −2,99×10⁻⁸ ✓; IC contém ΔJ e zero ✓ | **consistente internamente — não reproduzível (sem código)** |
| 2 | OOD: ΔJ = −4,22×10⁻⁸, IC = [−2,96×10⁻⁷, 2,08×10⁻⁷] → inconclusivo | aritmética ✓; IC ✓ | **consistente internamente** |
| 3 | λ = 1 foi o maior score entre os admissíveis (quadrático ≤ 0,505) | admissíveis {0: −0,00349691; 0,1: −0,00349692; 1: −0,00349666} → λ = 1 ✓ | **consistente internamente** |
| 4 | λ alto (10/100/1000) **elevou** a acurácia do atacante (0,50640 / 0,51270 / 0,51378 > 0,50111) | monotonia verificada ✓ | **consistente — refuta a expectativa simples de que mais penalidade = mais não-reconstrução** |
| 5 | OOD: atacante quadrático subiu ≈ 0,000713 | 0,50682 − 0,50611 = 0,00071 ✓ (diferença de arredondamento 3×10⁻⁶) | **consistente internamente** |
| 6 | "Cov(h,z) ≈ 0 não implica I(h,z) = 0" | conceitualmente correto e **reforçado pela execução do E10d**: representação com testes lineares ≈ acaso tem atacante neural em 55,6% | **aceita** |
| 7 | E10c vence magnitude/quadrática/janela nos dois splits; vs recorrente ID inconclusivo (+2,76×10⁻⁷) e OOD +8,27×10⁻⁷, `IC = [2,93×10⁻⁷, 1,37×10⁻⁶]` | ΔJ de OOD dentro do IC ✓; o restante depende de execução deles | **não reproduzível**; o documento já atribui o Δ OOD minúsculo à arquitetura ampliada, não à penalidade (λ=0 vs λ=1 foi nulo) — leitura aceita |

### E10d (código executado — números reproduzidos)

| # | alegação do documento | verificação | veredito |
|---|---|---|---|
| 8 | varredura de validação (5 linhas: score e atacante neural) | 10/10 idênticos ao JSON regenerado | **confirmada** |
| 9 | nenhum λ atingiu 0,515 → seleção por **fallback** = maior score → λ = 0,3 | 5/5 acima do limite; argmax do score = 0,3 ✓ | **confirmada — e mantida a designação "fallback", não "restrição satisfeita"** |
| 10 | ID sem adversário: J₀ = −0,00457451, L₀ = 0,00424898, lineares 0,49609, neural **0,55633** | 5/5 idênticos | **confirmada** |
| 11 | ID com adversário: J = −0,00455049, L = 0,00422571, neural **0,52216**; ΔJ = +2,4018×10⁻⁵, `IC = [2,0822×10⁻⁵, 2,7210×10⁻⁵]`, ΔA_neural = −0,03417 | 8/8 idênticos; IC inteiramente positivo ✓ | **confirmada** |
| 12 | OOD: J₀ = −0,00715446 → J = −0,00711585; neural 0,57977 → 0,55542; ΔJ = +3,8618×10⁻⁵, `IC = [3,3304×10⁻⁵, 4,4425×10⁻⁵]` | 8/8 idênticos; IC > 0 ✓ | **confirmada** |
| 13 | comparadores: E10d perde para magnitude, quadrática, janela e recorrente nos dois splits (todos os ICs negativos) | 16 scores/Δs idênticos; 8/8 conclusões "desfavoravel" ✓ | **confirmada** |
| 14 | "nenhuma semente vencida contra magnitude/quadrática/recorrente (ID) e 100% das sementes (OOD)" | `vitorias = 0,0` em 7 de 8; janela curta ID = 0,6% (única exceção, que o texto não inclui nessa lista) | **confirmada** |
| 15 | testes deles (3 nomes) | arquivos **fornecidos**: 3/3 executados aqui, `EXIT=0` | **confirmada** |
| 16 | **H1**: atacante neural encontra vazamento que os lineares não encontram | 0,55633 vs 0,49609 (ID) e 0,57977 vs 0,49513 (OOD) reproduzidos | **confirmada com ressalva (§4): os ataques lineares do E10d são degenerados — parte do contraste é do teste quebrado, não só da não-linearidade** |
| 17 | **H2**: adversarial reduz reconstrução neural (parcialmente) | 55,63→52,22 (ID) e 57,98→55,54 (OOD) reproduzidos; ambos ainda > 50% | **confirmada parcialmente, como o documento diz** |
| 18 | **H3**: privacidade sem perda de desempenho na mesma arquitetura | ΔJ > 0 com IC estritamente positivo nos dois splits | **confirmada nesta execução** |
| 19 | **H4**: recorrente adversarial supera controles convencionais fortes | **refutada**: 8/8 comparações desfavoráveis, ICs negativos | **refutação confirmada** — mesma direção do E10b (ciclo 7): controles fortes vencem de novo |

### E10e (sem código — checagem aritmética interna)

| # | alegação do documento | verificação | veredito |
|---|---|---|---|
| 20 | colunas de privacidade `P = 1 − 2·max(0, A−0,5)` (16 linhas ID/OOD) | 16/16 consistentes com as próprias acurácias (tolerância de arredondamento 1,5×10⁻⁵) | **consistente internamente — não reproduzível (sem código)** |
| 21 | melhor score em λ = 1 nos dois splits; melhor privacidade OOD em λ = 0,1 | recalculado ✓ | **consistente internamente** |
| 22 | fronteiras de Pareto: ID {0,3; 1}, OOD {0,1; 1} | recálculo de não-dominação a partir das tabelas: ID {0,3; 1} ✓, OOD {0,1; 1} ✓ | **consistente internamente** |
| 23 | execução reduzida (24 sementes, 240 passos, 24 sequências, 4 épocas) é **exploratória**; o teste participou da seleção | declaração do próprio documento (§9) | **aceita como limitação declarada — e adotada como disciplina (§5)** |

## 4. Achado novo desta auditoria: os ataques lineares do E10d não medem nada

Isto **não** está no documento — é produto da nossa verificação e muda a
leitura de vários números:

- No JSON publicado, o atacante **linear é exatamente igual ao quadrático em
  9/9 comparações** (5 linhas de validação + ID/OOD × sem/com adversário).
  Dois classificadores com features diferentes não dão a mesma acurácia ao
  acaso — a igualdade exata é assinatura de que ambos prevem a mesma coisa.
- A causa está no código deles (`attacks()`):
  `T = 2 * Y[:cut] - 1` com `Y` do tipo **uint8** — a subtração faz *wraparound*
  e `T` vira `{255, 1}` em vez de `{-1, +1}`. Ambos os alvos são positivos,
  então o ridge ajusta-se a prever **quase tudo positivo**: na prova que
  rodamos aqui, **> 99,5%** das previsões foram positivas e a "acurácia" do
  atacante ficou a 0,002 da **taxa base de Y = 1** (0,4854 vs 0,4875) — ou
  seja, igual ao que um classificador que ignora o estado alcançaria.
- No JSON publicado isso aparece como acurácias lineares entre 0,4951 e
  0,5010, todas ≈ taxa base. **"Linear ≈ acaso" no E10d não é evidência de
  não reconstrução: o teste é degenerado.**

Consequências, com a mesma honestidade da regra do projeto:

1. **H1 continua de pé, mas com ressalva** — o que prova que existe
   informação recuperável é o atacante **neural** (0,55633 ID / 0,57977 OOD
   sem adversário, acima de 0,5 por milhares de rótulos), não o contraste
   com um atacante que não ataca. O achado do documento ("um resíduo pode
   parecer não reconstrutivo sob testes lineares e ainda conservar estrutura
   para reconstrução não linear") fica **mais forte**: no E10c os testes
   lineares eram insuficientes, e no E10d eram *quebrados*.
2. **A E10c também é lida sob essa luz** — a "elevação do vazamento com λ
   alto" (0,50640–0,51378) veio de um atacante quadrático funcional
   (regressão com alvo real, sem wraparound), então aquela conclusão se
   mantém; mas toda comparação futura de "vazamento linear" precisa de um
   teste unitário de sanidade do classificador.
3. **Impacto no nosso trabalho:** a ressalva `docs/10` §6.4 ("≈ acaso vale
   para *esse* decodificador") ganha **evidência externa** — testes lineares
   podem estar quietos por estarem quebrados ou por não cobrirem a família.
   O nosso E10b usa decodificador de limiar por canal (não o ridge deles),
   então os números publicados não mudam; mas a pergunta "um atacante neural
   ou temporal acha o que o limiar não acha?" passa a ser pendência
   explícita: **P1.11** (§5).

A invariante que reproduz o bug está registrada no próprio teste
(`2 * np.array([0,1], uint8) - 1 → [255, 1]`), para que a ressalva não se
perca.

## 5. O que foi adotado

| o que | onde ficou |
|---|---|
| **E10d portado para o nosso código** — port fiel, determinístico (sementes 101/77/88/884), roda no `run_all` e na CI | `experimentos.py::e10d_controles()`, chave `E10d_controles` do `resultados.json` |
| **figura 11** — varredura da validação, ataque linear × neural, Δ adversarial e comparadores com IC | `figs/e10d_controles.png` |
| **2 testes novos (32 → 34)** — regressão das tabelas publicadas (com fallback e ressalva do atacante linear) + determinismo/Q4/disjunção de sementes | `tests/test_smoke.py` |
| **ressalva do docs/10 §6.4 reforçada** com a prova do E10d (testes lineares podem não medir nada) | `docs/10` §6.4 apontando para cá |
| **P1.11** — atacante **neural e temporal** contra os **nossos** estados (E10 float64 e ports de 24 bits), com o protocolo de 7 pontos do E10e §9 (sementes nunca vistas, ≥ 200, ICs, binomial contra 50%) | `docs/04` |
| **P2.7 atualizado com a lição do E10c externo** — a formulação linear de não reconstrução foi implementada de forma independente e deu **nulo**; a versão nossa deve ir direto para penalidade adversarial (caminho E10d/E10e) ou aceitar a nulidade como previsível e publicá-la | `docs/04` P2.7 |
| **"fallback ≠ restrição satisfeita"** — quando nenhum ponto atinge o limite, a seleção é declarada como fallback | `docs/11` §3 nº 9, `E10d_controles.protocolo` |
| **"conjunto de teste não participa da seleção"** — a lição metodológica do E10e vira reforço da nossa disciplina de pré-registro (P3.4) | `docs/04` P3.4, `docs/11` §3 nº 23 |
| **resultado negativo com a mesma proeminência** — H4 refutada (controles fortes vencem o E10d nos dois splits) publicada como veredito | `README.md`, `README.en.md` |

## 6. Ressalvas mantidas (o que NÃO foi adotado sem prova)

1. **E10c e E10e continuam não reproduzíveis por execução** — sem código
   não há o que rodar; suas alegações entram apenas como *consistência
   interna* das tabelas. Nenhum número deles virou chave do nosso JSON: os
   números que regredimos são só os do E10d (`E10d_controles`).
2. **E10c × controles do E10b** (Δ ≈ 6,34×10⁻⁵ ID etc.) não é reproduzível
   — o documento mesmo o trata como efeito pequeno e possivelmente de
   arquitetura; não citamos como fato.
3. **E10e é exploratória por construção** — 24 sementes e λ inspecionados no
   teste (declaração do próprio documento). Fronteiras de Pareto e a
   recomendação λ = 0,1 **não** valem como evidência confirmatória; qualquer
   E12/P2.7 precisa fixar λ antes e usar sementes nunca observadas.
4. **Ambiente deles continua sintético** (24 bits, hot-spots de variância) —
   a mesma ressalva do `docs/10` §6.5: as refutações valem dentro dele; a
   ponte para o nosso ambiente é **P1.10**, ainda aberta.
5. **H4 refuta o codificador do E10d, não a técnica adversarial** — a leitura
   do documento (sigmoidal + STE + gradiente truncado produziu estados menos
   eficientes que o recorrente linear do E10b) é coerente com os próprios
   números e é aceita como hipótese mecanística, não como fato provado.
6. **Nosso E10b não foi reavaliado com atacante neural** — os números
   "decodificador ≈ acaso" (0,4985–0,5018) permanecem escopados ao decodificador
   de limiar; medi-los com atacante neural/temporal é exatamente **P1.11**.
7. **O E10d não substitui o E11** (E10 com política aprendida, `docs/09` §8)
   nem o **P2.7** — são caminhos distintos na fila.

## 7. Números reproduzidos (`E10d_controles`)

Varredura de validação (semente dos λ só aqui; nota: nenhum atingiu o limite
0,515 — **seleção por fallback**, maior score):

| λ | score | atacante neural |
|---|---|---|
| 0 | −0,00447735 | 0,54342 |
| 0,01 | −0,00447714 | 0,54288 |
| 0,03 | −0,00447671 | 0,53667 |
| 0,1 | −0,00447100 | 0,53866 |
| **0,3** | **−0,00445562** | **0,52467** |

Efeito do treinamento adversarial (Δ pareado por semente, 160 sementes de
teste, IC95% bootstrap):

| split | ΔJ (adversarial − sem) | IC95% | neural sem → com | ΔA_neural |
|---|---|---|---|---|
| ID | **+2,4018×10⁻⁵** | [+2,0822×10⁻⁵, +2,7210×10⁻⁵] | 0,55633 → 0,52216 | −0,03417 |
| OOD | **+3,8618×10⁻⁵** | [+3,3304×10⁻⁵, +4,4425×10⁻⁵] | 0,57977 → 0,55542 | −0,02435 |

Comparadores fortes do E10b (Δ = E10d − controle; todos desfavoráveis):

| controle | score ID | Δ ID | score OOD | Δ OOD |
|---|---|---|---|---|
| EMA de magnitude | −0,003544 | −0,001006 | −0,005463 | −0,001653 |
| EMA quadrática | −0,003674 | −0,000876 | −0,005488 | −0,001627 |
| janela curta | −0,003710 | −0,000840 | −0,005329 | −0,001786 |
| recorrente E10b | **−0,003484** | −0,001067 | **−0,005171** | −0,001944 |
| E10d adversarial | −0,004550 | (ref.) | −0,007116 | (ref.) |

**Veredito publicado (com a mesma proeminência dos positivos):** o
treinamento adversarial **reduz reconstrução neural sem custo dentro da
própria arquitetura** (ΔJ > 0 com IC estritamente positivo nos dois splits,
H3), e o atacante neural **encontra conteúdo recuperável onde os testes
lineares medem acaso** (H1 — com a ressalva do §4: os lineares deles são
degenerados). Mas o E10d **perde para todos os controles fortes do E10b nos
dois splits** (H4 refutada: 8/8 comparações desfavoráveis, ICs negativos,
vitórias ≈ 0 — só 0,6% contra a janela curta no ID) e a reconstrução neural
permanece acima de
50% mesmo com adversário (H2 apenas parcial). A cadeia agora é: E10 mostra
vantagem contra memória assinada → E10b refuta a comparação fraca → E10c
mostra que covariância linear não basta → E10d mostra que atacante neural
acha o que os lineares não veem e que adversarial reduz (mas não vence os
controles) → E10e esboça a fronteira privacidade × utilidade (exploratória).

## 8. Pendências geradas por este ciclo

- **P1.11** (novo) — **atacante neural e temporal contra os nossos
  estados**: aplicar um atacante MLP (e um que veja `h_{t−k..t}`) ao estado
  do nosso E10 (6 float64) e aos ports de 24 bits (E10b/E10d), com o
  protocolo do E10e §9: sementes nunca observadas, ≥ 200, ICs para
  utilidade e reconstrução, teste binomial contra 50% — para responder se
  "decodificador ≈ acaso" sobrevive a um ataque não linear (`docs/04`).
- **P2.7 atualizado** — a versão linear de não reconstrução (E10c externo)
  já foi implementada de forma independente e resultou em **nulo**; o nosso
  P2.7 deve ser formulado desde já com penalidade adversarial (caminho
  E10d/E10e) ou aceitar que a nulidade é previsível e publicá-la como tal
  (`docs/04`).
- **P1.10 permanece** — controles fortes no **nosso** ambiente do E10; nada
  desta auditoria dispensa essa ponte.
- **E11 permanece** — E10 com política aprendida (`docs/09` §8); E10c/E10d/
  E10e são linhas paralelas, e um eventual experimento nosso que una
  recorrente forte + adversarial seria o candidato natural a **E12**
  (após P1.11 e P2.7).

---

## Summary (EN)

The fourth external audit ("MUTARIC ev 3 e 4") covered three experiments —
**E10c** (a *linear* non-reconstruction covariance penalty), **E10d**
(adversarial training with a neural attacker) and **E10e** (adversarial
training on the strong E10b recurrent state, a privacy–utility Pareto
curve). Only E10d shipped code: it was **executed here (170.6 s, exit 0)
and regenerated the published JSON with 0 differences across 129 numbers**;
its own test suite passed 3/3. The document's tables were checked with
**113/113 verifications** (E10d tables vs JSON, E10c/E10e internal
arithmetic — ΔJ, bootstrap CIs containing zero, λ-selection criterion,
`P = 1 − 2V` columns and Pareto recomputation). E10c and E10e have **no
code and remain unverifiable by execution**; only their internal
consistency passed. **E10d was ported** to `experimentos.py::e10d_controles()`
(key `E10d_controles`, figure `e10d_controles.png`, tests 32 → 34).

Verdicts: E10c's penalty is null (high λ even *increased* measured
leakage — refuting the simple expectation; `Cov ≈ 0` does not imply
`I ≈ 0`). E10d's own hypotheses: H1 **confirmed with a caveat of ours** —
the document's linear/quadratic attackers are **degenerate**: `T = 2Y−1`
on uint8 wraps to `{255,1}`, so the ridge predicts >99.5 % positive and
scores ≈ the base rate (linear == quadratic in 9/9 published comparisons);
the real evidence is the **neural attacker at 55.6 % ID / 58.0 % OOD**.
H2 partially confirmed (55.63→52.22, 57.98→55.54, still > 50 %). H3
confirmed in this run (ΔJ > 0 with strictly positive CIs in both splits).
**H4 refuted**: E10d loses to *all* strong E10b controls in both splits
(all CIs negative, ~0 % wins) — the same direction as our cycle-7 verdict.
λ was chosen by **fallback** (no λ met the 0.515 limit), honestly declared.
Adopted: the port above; a reinforced caveat on `docs/10` §6.4 (linear
tests may measure nothing); roadmap item **P1.11** (neural *and temporal*
attackers against *our* states, following E10e's 7-point confirmatory
protocol); **P2.7** updated with the lesson that the linear formulation was
independently implemented and came out null (escalate to adversarial).
Open: P1.8, P1.9, P1.10, P1.11, P2.6, P2.7; E11 (learned policy) remains.
Status: 34 tests, 11 figures, E1–E10 + E10b + E10d, docs/00–docs/11.
