# 07 — Documento de continuidade

> **Para quem retomar este trabalho** (inclusive eu-mesmo daqui a meses).
> Diz o estado atual, como verificar que nada quebrou, o que já está decidido
> (não reabrir sem prova) e qual é o próximo passo. Companheiro obrigatório de
> `docs/04_plano_desenvolvimento.md` (o plano) e `docs/08_historico_completo.md`
> (o que já passou).

---

## 1. Onde isto parou (04/10/2026)

| item | estado |
|---|---|
| Repositório | **`github.com/ebiossanto/IA-RESEARCH-MUTARIC`** (**público** desde 04/10/2026), branch `main` |
| Código | pacote `ricemotions/` — 6 módulos, nenhum com I/O fora de `experimentos.py` |
| Experimentos | **E1–E10 + E10b + E10d + E10e_repl** (E1–E4 núcleo, E5 resíduo, E6 agência, E7–E9 verificação externa MutaCore, **E10** paridade de orçamento — auditoria MUTARIC ev, **E10b** controles fortes de memória — auditoria MUTARIC ev 2, **E10d** adversarial + atacante neural — auditoria MUTARIC ev 3/4, **E10e_repl** réplica nossa do protocolo de Pareto — auditorias MUTARIC ev 5/6) |
| Testes | **36/36** (`python tests/test_smoke.py`), regressão dos números publicados |
| CI | GitHub Actions, matriz **Windows + Linux** (`.github/workflows/ci.yml`, P0.5) |
| Figuras | 12 em `figs/` (geradas, determinísticas — o diff deve ser vazio ao regerar) |
| Resultados | `resultados/resultados.json` — fonte única de todos os números citados |
| Coleta real | `resultados/maquina.json` + `resultados/telemetria_real.json` — informação desta máquina, **não regressada** (`--telemetria`, `docs/09` §6) |
| Documentos | `docs/00` a `docs/12` (índice, arquitetura, achados, ponte, plano, resíduo/agência, MutaCore, continuidade, histórico, **auditoria MUTARIC ev**, **auditoria MUTARIC ev 2**, **auditoria MUTARIC ev 3/4**, **auditorias MUTARIC ev 5/6**) |
| Estado do texto | **protótipo exploratório**: números descritivos, sem IC nem teste de hipótese |

## 2. Retomar em 10 minutos

```bash
git clone https://github.com/ebiossanto/IA-RESEARCH-MUTARIC.git
cd IA-RESEARCH-MUTARIC
pip install -r requirements.txt

python run_all.py --so-testes    # 36 testes, minutos — faz isto PRIMEIRO
python run_all.py                # testes + E1-E10 + E10b + E10d + E10e_repl
                                 # + figuras (~15 min)
python -m ricemotions.experimentos --telemetria   # coleta REAL da máquina (opcional,
                                                  # requer psutil; grava arquivos próprios)
```

Se os **36 testes** passam, o trabalho está exatamente como foi publicado.
Se algum falhar, **não edite o teste para fazer passar**: a falha diz qual número
publicado mudou — leia `docs/02` e `docs/06` antes de decidir qualquer coisa.

Ordem de leitura do repositório: `README.md` → `docs/00_indice.md` → o que o
índice indicar. Para o estado do projeto em uma página: `docs/04`.

## 3. O que já está decidido (não reabrir sem prova)

Estas regras nasceram de erro ou de refutação documentada; mudá-las exige
reprodução numérica, como em `docs/06`.

1. **Nada é aceito por leitura.** Toda afirmação externa (ou interna) é
   reproduzida numericamente antes de virar código ou texto. Método do ciclo
   MutaCore (`docs/06` §1).
2. **Os números publicados não mudam silenciosamente.** Estão em
   `resultados/resultados.json` e são regressados pelos testes. Mudou número ⇒
   documentar em `docs/02`/`docs/06` **antes** de atualizar.
3. **I/O de disco só em `ricemotions/experimentos.py`.** O núcleo (`mundo`,
   `glifo`, `residuo`, `agente`, `homeostase`) é puro e testável.
4. **Telemetria de hardware (`psutil`) nunca roda dentro de `run_all.py` ou dos
   testes** — é não-determinística. Existe como função opcional
   (`homeostase.telemetria`) e como coleta **opt-in**
   (`python -m ricemotions.experimentos --telemetria`), que grava
   `resultados/maquina.json` e `resultados/telemetria_real.json` marcados
   `deterministico: false` e **nunca regressados** (`docs/09` §3, correção 1).
5. **O mundo é roteirizado** (`mundo.py` escreve as procedências à mão) e o leitor
   **relê o que o escritor gravou literalmente**. Qualquer número de E1–E4 carrega
   essa ressalva (`docs/02`, `docs/03` L6) — ela deve ir junto com o número.
6. **Recusas firmes, com prova registrada**: cifra por resíduo (16,6 bits —
   `docs/06` §5), benchmark de sobrevivência como validação de emoção (0% de ganho
   e morte impossível — `docs/06` §4), telemetria ligada por padrão (`docs/06` §9),
   espalhamento Walsh sem decodificador (vira item futuro P1.7).
7. **Resultado nulo publicado com a mesma proeminência do positivo** — é critério
   de pronto do projeto (`docs/04`).
8. **Veio sem código?** Então só há dois caminhos honestos: checagem aritmética
   interna (tabelas × JSON × CSV, fórmulas, estatísticas recalculadas) e, se o
   protocolo for descrito, uma **replicação própria declarada como nossa** —
   nunca apresentada como reprodução dos números deles (`docs/12` §2).

## 4. Próximo passo (em ordem)

A fila completa e detalhada está em `docs/04` (P1, P2, P3, P4), com critério de aceite
por item. A ordem recomendada para retomar:

1. **P1.1 — baseline séria**: regressão logística/MLP sobre o episódio achatado e
   sobre o glifo achatado, mesma divisão, `balanced_acc` ± IC (bootstrap).
   *Pronto quando:* tabela com 4+ métodos. É o que dá valor ao 0,919.
2. **P1.2 — teste de hipótese pareado**: relacional vs `nivel+delta` com IC;
   se o IC incluir 0, o resultado é declarado **nulo**.
3. **P1.3 — transformações perceptivas reais** (corte, redimensionamento,
   JPEG/quantização, oclusão) na mesma tabela de robustez.
4. Depois P1.4–P1.7 (neutro, ancoras, graus de liberdade, carga como canal) e
   **P2.1**, trocar `mundo.episode()` por `teoa/core.py` de verdade.

> **P0.1–P0.5 estão fechados** (testes, codebook de isomorfismo, leitor soft,
> curva × σ, CI) e a **auditoria MUTARIC ev** foi analisada com provas
> (`docs/09`: 5 correções adotadas, E10 implementado, coleta real da máquina).
> As correções 4 e 5 viraram dois itens novos na fila: **P1.9** (protocolo
> hierárquico contra pseudorreplicação) e **P2.6** (agente sem evento externo
> sintético). A fila de prioridade continua P1.1 → P1.2 → P1.3.
>
> A **segunda auditoria (MUTARIC ev 2)** também foi analisada com provas
> (`docs/10`): o `e10b.py` deles executado aqui com **58/58 números
> reproduzidos** e portado como **E10b** — veredito publicado: *contra
> memórias fortes de igual orçamento (24 bits) o resíduo não vence* (melhor
> agente: recorrente aprendido; ICs fora de zero nos dois splits). Daí saíram
> **P1.10** (controles fortes + OOD + IC bootstrap no nosso ambiente do E10)
> e **P2.7** (E10c, resíduo preditivo com não reconstrução).
>
> **A terceira auditoria (MUTARIC ev 3/4)** também foi analisada com provas
> (`docs/11`): o `e10d.py` deles executado aqui regenerou o JSON publicado
> **idêntico (0 diferenças em 129 números)** e portado como **E10d** —
> vereditos publicados: *o treinamento adversarial reduz reconstrução neural
> sem custo (ΔJ > 0, ICs estritamente positivos), mas o E10d perde para
> todos os controles fortes do E10b nos dois splits* (H4 refutada), e os
> **ataques lineares deles são degenerados** (uint8 em `2*Y−1` ⇒ alvos
> `{255,1}`; linear == quadrático em 9/9). E10c e E10e vieram **sem código**
> — só checagem aritmética interna. Daí saíram **P1.11** (atacante neural e
> temporal contra os nossos estados) e a atualização de **P2.7** (a versão
> linear de não reconstrução já foi implementada de forma independente e deu
> nulo — formular já com penalidade adversarial).
>
> **A quarta auditoria (MUTARIC ev 5 / ev 6)** também foi analisada
> com provas (`docs/12`): o zip veio **só com saídas, sem código** →
> **286/286 checagens aritméticas** (tabelas × JSON × CSV, fórmulas de P,
> fronteiras de Pareto recalculadas, Welch e z do ev 6 recalculados com
> `scipy`) e uma **replicação nossa executada neste terminal**
> (**E10e_repl**, mesmas 200 sementes do ev 5, 163,6 s, pareada por semente).
> Vereditos publicados: *o Pareto ID deles {0,3; 1} está contido no nosso;
> o Pareto OOD exato **não se repetiu** (o nosso fica na mesma prateleira
> P = 1 de λ pequeno, ponto diferente — publicado com a mesma proeminência);
> λ = 1 é o melhor score ID e o pior nos outros três cantos (privacidade ID,
> score e privacidade OOD — confirmado na réplica), e o maior vazamento OOD
> de λ = 1 foi confirmado
> com o **teste pareado por semente que o ev 6 não pôde fazer** porque não
> salvou o dado*. Daí saíram: reforço de **P3.4** (fixar λ antes do teste —
> a própria auditoria perdeu a fronteira OOD entre rodadas), selo de
> confirmação em **P1.9** (o ev 6 §5 escreveu a mesma advertência nossa de
> pseudorreplicação) e a disciplina de **salvar score e acurácia do atacante
> por semente** como exigência explícita.
>
> **Objetivo novo (05/10/2026, sem números):** o material externo
> `_MUTARIC Jev.md` **e o pacote `JEV_IA_MUTARIC_CONTINUIDADE.zip`** (ciclo 11,
> analisados em `docs/13`) propõem o **sistema JEV-IA-MUTARIC** — o Jev como
> camada probabilística de decisão sobre o estado MUTARIC (*LLM explica · Jev
> decide · MUTARIC regula · Supervisor limita*) — com o experimento
> **`E11-JEV`** fechado em **6 condições C0–C5**, 23 métricas e H1–H4.
> Adotado como **P4** em `docs/04`: contrato puro `decision_state()` (schema
> `jev-mutaric-1.0`), harness **sem Jev** (`MockJevProvider`, **λ=0,003
> congelado**, 200 sementes novas), atacante semântico (estende a P1.11),
> calibração ECE/Brier e formalização do **RDSP** (P4.7) — **nenhuma alegação
> sobre o Jev está verificada** (sem acesso ao modelo; as 7 recusas da §9 do
> `_MUTARIC Jev.md` viraram regra do projeto). **Lista de tarefas: `docs/13` §5.**

## 5. Pendências que vivem fora deste repositório

| pendency | onde | o que fazer quando chegar |
|---|---|---|
| Repositório **PIXEL** (RIC original) | `docs/03` §5 — `Desktop/PIXEL` vazio, sem repo na conta | preencher a URL e revisar as 4 correspondências (feature, τ, `d_I`, "1 grafo único") |
| `teoa/core.py` de verdade | `Desktop/Emoções/` | P2.1: adaptador `estado → (6,32)` e repetir E1–E4 |
| Documento `MUTACORE _ RIC.md` | fora do repo (anexo do usuário) | já analisado integralmente em `docs/06`; só reabrir se houver código novo anexado |
| Documento `MUTARIC ev.md` | fora do repo (anexo do usuário) | já analisado integralmente em `docs/09` (5 correções + E10 + coleta); só reabrir se houver nova versão |
| Documento `MUTARIC ev 2.md` + `e10b.py` | fora do repo (pasta `mutaric b/MUTARIC_E10b/` no Desktop) | já analisado e reproduzido em `docs/10` (E10b portado, 58/58); só reabrir se chegar o `e10.py`/os testes deles, que ficaram **não verificáveis** |
| Documento `MUTARIC ev 3 e 4.md` + `MUTARIC_E10d.zip` | fora do repo (pasta `IA-RESEARCH-MUTARIC-main/` no Desktop) | já analisado em `docs/11` (E10d portado, JSON idêntico); E10c ficou **não reproduzível** — só reabrir se chegar o código deles |
| `MUTARIC ev 5.md` + `MUTARIC ev 6.md` + `MUTARIC_E10e_200_SEMENTES.zip` | fora do repo (mesma pasta `IA-RESEARCH-MUTARIC-main/`) | já analisado em `docs/12` (286/286 + réplica `E10e_repl` aqui); o zip **não tem código** — se chegar o `e10e.py` deles, executar e cruzar com o JSON (a checagem aritmética inteira vira reprodução de verdade) |
| `_MUTARIC Jev.md` | fora do repo (mesma pasta `IA-RESEARCH-MUTARIC-main/`) | já adotado como **objetivo P4 — sistema JEV-IA-MUTARIC** (`docs/04`, 05/10/2026); reabrir quando houver **acesso ao Jev** — aí P4.3 (adaptador) e P4.4 (verificação das alegações) deixam de estar bloqueados |
| `JEV_IA_MUTARIC_CONTINUIDADE.zip` | fora do repo (em `Downloads\`) | analisado em `docs/13` (ciclo 11): retrato do nosso projeto conferido, protocolo `E11-JEV` **fechado** (6 condições C0–C5, λ=0,003 congelado, 200 sementes novas, Holm), **RDSP** e atacante semântico — **veio sem código**; se chegar código (`mock`/`e11_jev.py`), executar e cruzar |
| Licença do repositório | não definida | decidir antes de tornar público |

## 6. Checklist para adicionar um experimento (E11) sem quebrar nada

1. Função nova em `ricemotions/experimentos.py`, seeds explícitas
   (`np.random.default_rng(<n>Fixo)`), sem I/O fora de `figuras()`/`main()`.
2. Chave nova em `resultados/resultados.json` — nunca sobrescrever chaves antigas.
3. Teste de regressão em `tests/test_smoke.py` que **afirme** o número novo.
4. Figura nova (se fizer sentido) listada em `README.md`, `README.en.md` e
   `docs/01` §6.
5. Linha nova na tabela de experimentos de `docs/01` §5 + seção no documento
   adequado.
6. Rodar `python run_all.py` completo e conferir `git diff` em `figs/` e
   `resultados/`: só o que era esperado pode ter mudado.
7. Contagem de testes atualizada em `README.md`, `README.en.md`, `docs/01` e
   `docs/04` (P0.1).

## 7. Riscos que quem vier precisa saber

- **Quatro limites** listados no `README.md` (mundo roteirizado, leitor literal,
  parâmetros pós-hoc, `text_to_digits` perde bytes nulos iniciais).
- **Limitações da análise MutaCore** em `docs/06` §10 (o documento não anexou
  código; o E7 isola o efeito nos níveis; a força bruta varre `[0,1)`).
- **Escolhas pós-hoc não listadas** (P1.6): parte delas é conhecida, parte não —
  isso é pendência aberta e deve ser resolvida antes de qualquer afirmação
  confirmatória.
- O repositório é **público** desde 04/10/2026 (pedido do autor). Pendência que
  acompanha essa decisão: **P1.6** (graus de liberdade do pesquisador) segue aberta —
  se algum número publicado for revisto, a mudança deve ser anunciada no mesmo
  lugar onde o número foi publicado.

---

## Summary (EN)

This document is the **hand-off**: where the work stopped (04/10/2026), how to
resume in 10 minutes (`pip install -r requirements.txt` → `python run_all.py
--so-testes` → 36/36), and what is already decided and must not be reopened
without numerical reproduction. Repository:
`github.com/ebiossanto/IA-RESEARCH-MUTARIC` (public, branch `main`), CI on
Windows + Linux. Experiments are now **E1–E10 + E10b + E10d + E10e_repl**; the
external audit "MUTARIC ev" was verified claim by claim in `docs/09` (five
corrections adopted, E10 built, real telemetry from this machine collected into
non-regressed files), the second audit "MUTARIC ev 2" in `docs/10` (its
`e10b.py` run here with 58/58 numbers reproduced and ported as E10b:
**the residue does not beat strong memories of equal budget** — refutation
published with the same prominence), the third audit "MUTARIC ev 3/4" in
`docs/11` (its `e10d.py` run here regenerating the published JSON **identical
— 0 differences in 129 numbers** — and ported as E10d: adversarial training
reduces neural reconstruction without cost **but loses to every strong
control**; the document's linear attackers were found **degenerate**
(uint8 wraparound), and E10c shipped no code), and the fourth package
"MUTARIC ev 5 / ev 6" in `docs/12` (**outputs only — no code**): **286/286
arithmetic checks** (document × JSON × CSV, Pareto recomputed, Welch and
z-tests recomputed with `scipy`) plus **our own replication of the Pareto
protocol executed on this terminal** (`E10e_repl`, the same 200 seeds,
paired per seed): the ID Pareto of theirs is contained in ours, **the exact
OOD Pareto did not repeat** (same structure, different point — published
with the same prominence), and λ = 1's larger leakage was confirmed with
the paired per-seed test ev 6 could not run. On 05/10/2026 a **new objective**
was registered without new numbers: the **JEV-IA-MUTARIC system** (external
`_MUTARIC Jev.md` **plus the package `JEV_IA_MUTARIC_CONTINUIDADE.zip`** — 6
files, **no code**, analysed in `docs/13` = cycle 11, which checked their
picture of our project: 2 stale numbers and 1 conclusion repeated without our
test-dependent caveat). Jev is a probabilistic decision layer over the MUTARIC
state (*LLM explains · Jev decides · MUTARIC regulates · Supervisor limits*)
and **`E11-JEV`** is now frozen at **6 conditions C0–C5**, 23 metrics, H1–H4,
adopted as **P4** in `docs/04` (pure `decision_state()` contract
`jev-mutaric-1.0`, harness running without Jev — mock provider, λ = 0,003
frozen, 200 new seeds —, semantic attacker extending P1.11, ECE/Brier
calibration, RDSP formalization; **no claim about Jev verified** — no access
to the model, and the §9 caveats became project rules). Task list: `docs/13`
§5. The next
concrete step is still **P1.1** (serious baselines with bootstrap CIs), then
P1.2 (paired hypothesis test) and P1.3 (perceptual transformations); P0.1–P0.5
are closed. External pendencies live outside this repo: the PIXEL repository
(`docs/03` §5) and the real `teoa/core.py` (P2.1). Section 6 is a step-by-step
checklist for adding experiment E11 without breaking the published numbers;
section 7 lists the risks a newcomer must know.
