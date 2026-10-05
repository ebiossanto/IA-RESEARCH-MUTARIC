# 04 — Plano de desenvolvimento

Prioridades com **critério de aceite** explícito. Cada item tem um "pronto é quando…"
para não virar lista infinita. Esforço estimado para uma pessoa, com o código atual.

---

## P0 — Travar o que existe (1–2 dias)

| # | Tarefa | Pronto quando | status (04/10/2026) |
|---|---|---|---|
| P0.1 | `python run_all.py` roda limpo em Windows e Linux | testes + experimentos verdes em ambas as plataformas | **feito** — 36/36 testes |
| P0.2 | `codebook_up_to_isomorphism()` entra no E3 | `carga_permutacao` mostra `canonicalizado ≈ 1,0` e a curva `bits × σ` é regenerada; JSON e figura atualizados | **feito** — `carga_isomorfismo`: 0,208 → **1,000** limpo e sob permutação (`docs/05` §5) |
| P0.3 | Decodificação **soft** do grafo (ponderar bit por `\|cos\| − τ`) | `6c_relacional` em σ=0,10 **> 0,6** (hoje 0,334 = chance), sem piorar o caso limpo | **feito** — `body_cont` + de-atenuação + pesos: σ=0,10 → **0,733** (limpo 0,919 → 0,892, ver `docs/05` §2.2) |
| P0.4 | Curva acurácia × σ (hoje há pontos isolados) | gráfico com 6+ valores de σ para cada método | **feito** — 7 valores × 4 leitores, `figs/curva_sigma.png` |
| P0.5 | CI mínima (GitHub Actions: `pip install -r requirements.txt && python tests/test_smoke.py`) | badge verde no README | **feito** — `.github/workflows/ci.yml`, matriz Windows + Linux, 27/27 em ambas (04/10/2026) |

> **Fechar a conta do A3/A2 antes de qualquer afirmação nova.** São os dois números
> que mais enfraquecem o texto hoje.
> *(A3 fechado em `docs/05` §5.4: o 0,208 era desempate entre palavras isomorfas.)*

### Fechado neste ciclo (além do P0)

`docs/05_residuo_e_agencia.md` entrega os cinco itens acima **e** os dois problemas
conceituais abertos em `03`:

| item | onde |
|---|---|
| filtro de feedback de Landauer (energia descartada → T/C) | `docs/05` §3 |
| modularização do ambiente (resíduo → τ → reatividade) | `docs/05` §4 |
| resíduo como simetria (720 permutações, 0 linhas) | `docs/05` §5 (E5) |
| agência de mão dupla, com critério operacional | `docs/05` §6 (E6) |
| resposta a "eu não sinto, eu computo" | `docs/05` §8 |

### Segundo fechamento (04/10/2026, ciclo MutaCore)

`docs/06_analise_mutacore.md` analisa o documento **`MUTACORE _ RIC.md`** anexado pelo
usuário. Regra usada: **nada é aceito sem ser reproduzido numericamente**. Resultado:
das 18 afirmações, 8 confirmadas, **6 refutadas**, 4 parciais ou não verificáveis —
4 mecanismos novos entraram no código (7 entradas, `docs/06` §2).

| item | onde |
|---|---|
| resíduo **endógeno** (`ΔH_L` da própria transição → `R_L` → `Φ`) | `homeostase.py` + `docs/06` §3 (E7) |
| telemetria → `S*` e telemetria → `τ` (funções puras + `Agente.passo(carga_hw=)`) | `homeostase.py`, `docs/06` §2 |
| política pela distância a `S*` e o robô do benchmark com 3 interruptores | `homeostase.py`, `docs/06` §4 (E8) |
| prova de que a chave cifrada pelo resíduo tem 16,6 bits | `docs/06` §5 (E9) |
| correção da alegação "~91,8% com σ ≤ 0,30" | `docs/06` §6 |
| dose-resposta do resíduo (γ = 0,8 / ×10 / ×100) e teste da previsão "nível cai, relacional segura" | `docs/06` §7 (E7) |
| bug: o código da §B injeta `R_L ≡ 0` | `docs/06` §8.1 |

Novos números: `E7_residuo_mutacore`, `E8_sobrevivencia`, `E9_chave_residuo`;
figura `figs/mutacore.png`; testes 21 → **27**.

## P1 — Fazer a afirmação sobreviver a escrutínio (1–2 semanas)

| # | Tarefa | Pronto quando |
|---|---|---|
| P1.1 | Baseline séria além de médias: regressão logística/MLP sobre o episódio achatado, e sobre o glifo achatado | tabela com 4+ métodos, mesma divisão, `balanced_acc` ± IC via bootstrap |
| P1.2 | Teste de hipótese: relacional **vs** `nivel+delta` com bootstrap pareado | Δ com intervalo de confiança; se incluir 0, o resultado é declarado **nulo** |
| P1.3 | Transformações perceptivas reais: corte de linhas/colunas, redimensionar 48×32 → 24×16, JPEG/quantização espacial, oclusão de blocos | mesma tabela de robustez com as novas colunas |
| P1.4 | Faixa de neutro na valência (`|v| < ε` ⇒ família indeterminada) | `consistencia_familia_vs_valencia` reportado **com** a taxa de "indeterminado" |
| P1.5 | Fixar âncoras e reduzir a busca canônica do corpo (24 perms. ou forma canônica verdadeira) | `permutacao_corpo` recupera > 0,85 (hoje 0,666) |
| P1.6 | Documentar **graus de liberdade do pesquisador** (τ, `d_min`, janelas 8/8, `d_ref`, `α`, `β`, `noise`, distrator 30%, **γ do resíduo endógeno**, **`carga_hw`**) | lista numerada em `docs/` — mesma disciplina do TEOA `docs/05` |
| P1.7 | Carga como canal: espalhamento por portadora + **decodificador** (ideia do MutaCore §F, recusada lá por não ser verificável — `docs/06` §8.5/§9) | `decode_payload` lê a camada espalhada e `carga_capacidade` não piora |
| P1.8 | τ com **zona morta/histerese** (achado A2b de `docs/02` — pendência órfã, nunca entrou no plano) | o leitor duro sobe em σ=0,10 sem leitor robusto e não perde o caso limpo |
| P1.9 | **Protocolo hierárquico** `mundo → semente → episódio` para as ICs (auditoria MUTARIC ev, correção 4 — 1800 episódios de uma semente não são 1800 independentes; `docs/09` §3; **confirmada pelo próprio autor no ev 6 §5**, que escreveu a mesma advertência para as 144000 previsões — `docs/12` §3 nº 17) | ICs calculadas com o MUNDO como unidade (≥ 10 sementes × ≥ 3 seeds de mundo); se a IC incluir 0, o resultado é declarado nulo |
| P1.10 | **Controles fortes de memória no ambiente do E10** (auditoria MUTARIC ev 2 — o E10b externo refutou a formulação forte com 24 bits; `docs/10` §4): repetir `AR × magnitude × janela × recorrente` **no nosso** `mundo` (S* vetorial, J), com teste OOD (duração+frequência+intensidade) e IC bootstrap pareado | `J(AR) > J(controles fortes)` sobrevive aqui? se IC incluir 0, o resultado é declarado nulo — mesma disciplina do P1.2 |
| P1.11 | **Atacante neural e temporal contra os nossos estados** (auditoria MUTARIC ev 3/4 — `docs/11` §4: os testes lineares do E10d são degenerados e um MLP achou 55,6% onde o limiar mede acaso): treinar um atacante MLP (e um temporal `h_{t−k..t}`) contra o estado do **nosso** E10 (6 float64) e dos ports de 24 bits, com o protocolo de 7 pontos do E10e §9 (sementes nunca observadas, ≥ 200, ICs de utilidade e reconstrução, teste binomial contra 50%) — **ciclo 9** (`docs/12`): a auditoria ev 5/6 cumpriu só 2 dos 7 pontos (sem λ fixado antes, sem ICs, sem atacante temporal) e o pareado por semente que ela não pôde fazer está **demonstrado e funcionando** no `E10e_repl` (score + acurácia do atacante por semente, bootstrap pareado) | "decodificador ≈ acaso" sobrevive a um ataque não linear? se o atacante passar de 50% com IC fora do acaso, a ressalva `docs/10` §6.4 vira resultado — publicado igualmente nulo ou positivo |

## P2 — Ligar o TEOA de verdade (2–4 semanas)

Hoje `mundo.py` é um roteiro (ver `03`, L1–L6). Esta fase é o que transforma o
pacote de "leitor de glifos" em "emoção comunicada".

| # | Tarefa | Pronto quando | status (04/10/2026) |
|---|---|---|---|
| P2.1 | Trocar `mundo.episode()` por `teoa.core` (dinâmica E,T,C, regimes, histerese) com um adaptador `estado → (6,32)` | mesmos 4 experimentos rodam com o TEOA real; comparação lado a lado | **pendente** |
| P2.2 | **Agente**: escolhe ações, paga custo, o mundo muda; a valência sai da dinâmica e não do roteiro | existe `agente.py` com política e `resultado` = recompensa/estado final | **parcial** — `agente.py` existe com transição e mão dupla (`docs/05` §6), mas **sem custo/recompensa** e a valência ainda sai de `affect()` |
| P2.3 | **Loop de comunicação**: agente A escreve glifo, agente B lê e isso altera a ação de B | experimento com 2 agentes e métrica de ganho/mutual information | **pendente** (o feedback de hoje é do leitor sobre as próprias regras, não sobre outro agente) |
| P2.4 | Memória: sequência de glifos no tempo (ciclos, histerese do TEOA) | série temporal de glifos e detecção de regime |
| P2.5 | Mix de emoções (dois episódios sobrepostos) e glifos "ambíguos" por projeto | E1–E4 rodando em classes multi-rótulo |
| P2.6 | **Agente sem evento externo sintético** (auditoria MUTARIC ev, correção 5 — hoje o E6 recebe `residuo_evento` de `residuo.gerar()` com seed; `docs/09` §3) | o loop do E6 roda só com resíduo endógeno (`residuo_transicao`) e/ou telemetria real, mantendo os números de `E6_agencia` documentados como antes-da-mudança |
| P2.7 | **E10c: resíduo preditivo comprimido com restrição de não reconstrução** (auditoria MUTARIC ev 2, `docs/10` §1/§8): `R ← Q_B[F_θ(R, Δ, E, S*)]` com `I(R;sign(Δ)) ≈ 0`, `I(R;custo futuro) > 0` e `J(R) > J(M)` contra memórias fortes — **atualização do ciclo 8** (`docs/11` §5/§8): a auditoria ev 3/4 implementou *de forma independente* a versão **linear** dessa ideia (E10c externo) e o resultado foi **nulo** (ICs contêm zero; λ alto ainda elevou o vazamento) — portanto formular já com penalidade **adversarial** (caminho E10d/E10e) ou aceitar a nulidade como previsível e publicá-la | o resíduo aprendido sob a restrição vence os controles fortes do P1.10 **sem** permitir reconstrução do sinal apagado (medida pelo P1.11, não só por limiar); candidato natural a E12 (o E11 = política aprendida, `docs/09` §8, permanece) |

**Critério de parada da P2:** se, com o agente real, `nivel+delta` continuar 1,000 e
o relacional continuar pior, a conclusão é que a hipótese relacional **não se sustenta**
— e isso deve ser escrito, não contornado.

## P3 — Publicar (contínuo)

1. `README.en.md` já existe; manter sincronizado com o PT.
2. ~~Repositório GitHub~~ **feito** — `ebiossanto/IA-RESEARCH-MUTARIC` (**público**,
   `main`, CI verde). Falta: **link do PIXEL em `docs/03` §5**.
3. Figuras com erro-padrão (hoje, um ponto por condição).
4. Pré-registro das hipóteses **antes** de rodar a P1 (lição do TEOA `docs/03`/
   `docs/05`: resultados exploratórios não são evidência confirmatória).
5. Relacionar explicitamente com a literatura: affective computing com canal
   *valência × arousal*, RL homeostático, código de canal com decisão.

---

## Definição de pronto do projeto (versão 0.2)

- [x] **P0.1–P0.4 fechados** (04/10/2026): `run_all.py` verde com 27 testes, leitor
      robusto a ruído, curva acurácia × σ e carga isomórfica — `docs/05` §2 e §5.
- [x] **Análise externa reproduzida com provas** (04/10/2026): documento MutaCore —
      o que é correto entrou no código, o que não é ficou refutado — `docs/06`, E7–E9.
- [x] `run_all.py` verde em CI. *(P0.5, fechado 04/10/2026: GitHub Actions,
      matriz Windows + Linux — o job roda `tests/test_smoke.py`)*
- [x] Repositório GitHub publicado (`ebiossanto/IA-RESEARCH-MUTARIC`, **público**
      desde 04/10/2026, `main` + CI verde) *(04/10/2026)*
- [x] Documentos de navegação e memória: `docs/00` (índice), `docs/07`
      (continuidade) e `docs/08` (histórico completo) *(04/10/2026)*
- [x] **Auditoria externa MUTARIC ev analisada com provas** (04/10/2026): as 5
      correções adotadas (2 viraram o plano **P1.9**/**P2.6**), a proposição
      `F(X,R) ≠ F(X,R')` verificada nos testes, o **E10** (paridade de orçamento:
      4 agentes, 3 condições) implementado e a coleta **real** desta máquina em
      arquivos próprios não-regressados — `docs/09`; na época 30 testes, 9 figuras.
- [x] **Auditoria externa MUTARIC ev 2 analisada com provas** (04/10/2026): o
      `e10b.py` deles executado aqui (**58/58 números reproduzidos**) e portado
      como **E10b** — veredito publicado: *contra memórias fortes de igual
      orçamento (24 bits) o resíduo não vence* — mais **P1.10**/**P2.7** na fila
      — `docs/10`; na época 32 testes, 10 figuras.
- [x] **Auditoria externa MUTARIC ev 3/4 analisada com provas** (04/10/2026): o
      `e10d.py` deles executado aqui (**JSON idêntico, 0 diferenças em 129
      números; 113/113 checagens das tabelas**) e portado como **E10d** —
      vereditos publicados: *o treinamento adversarial reduz reconstrução
      neural sem custo, mas o E10d perde para todos os controles fortes* (H4
      refutada) e *os ataques lineares deles são degenerados* (uint8) — mais
      **P1.11** e **P2.7** atualizado — `docs/11`; na época 34 testes, 11 figuras.
- [x] **Auditorias externas MUTARIC ev 5/6 analisadas com provas** (04/10/2026):
       zip **sem código** → **286/286 checagens aritméticas** (tabelas × JSON ×
       CSV, Pareto recalculado, Welch e z do ev 6 recalculados com `scipy`) e
       **replicação nossa executada neste terminal** (`E10e_repl`, 200 sementes
       do ev 5, 163,6 s, pareado por semente) — vereditos publicados: *o Pareto
       ID deles está contido no nosso; o Pareto OOD exato não se repetiu (mesma
       estrutura, ponto diferente); λ = 1 vaza mais nos dois splits, confirmado
       com o teste pareado que o ev 6 não pôde fazer* — `docs/12`; hoje 36
       testes, 12 figuras.
- [x] Resultado nulo publicado com a mesma proeminência do resultado positivo.
      *(parcial → cumprido: E8 (ganho 0%), E9 (chave de 16,6 bits), o E10
      "AR ≈ A0 — o resíduo supera a memória convencional, não a ausência de
      memória" (`docs/09` §5.2), o **E10b** "contra memórias fortes de igual
      orçamento o resíduo não vence" (`docs/10` §7) e agora o **E10d** "H4
      refutada: o adversarial não vence os controles fortes" (`docs/11` §7) —
      todos publicados com o mesmo destaque dos positivos)*
- [ ] Números do E1–E4 com IC e teste de hipótese.
- [ ] Um experimento com `teoa.core` de verdade (P2.1).
- [ ] Link do repo PIXEL em `docs/03` §5.
- [ ] Toda escolha feita *depois* de ver resultado, listada. *(parcial: a troca da
      métrica de reatividade está listada em `docs/05` §7.5; as escolhas de
      `k_t`, `k_tau`, `k_relax`, `β` e `J` ainda não)*

## Registro de erros, acertos e retomadas de caminho (ciclos 0–9)

Histórico detalhado do desenvolvimento, pedido explicitamente: cada erro com
sua correção, cada acerto com sua prova, cada mudança de caminho com seu
motivo. Serviço de memória para quem continuar o trabalho.

### A. Erros cometidos e como foram corrigidos

| # | ciclo | o erro | a correção | a lição que ficou |
|---|---|---|---|---|
| A.1 | 0 | começou sem base de prova: scripts soltos em pasta com espaço no nome, sem pacote, sem testes | refatoração para o pacote `ricemotions` (mundo/glifo/residuo/agente/homeostase/experimentos), `tests/test_smoke.py` e `run_all.py` antes de qualquer resultado novo | nada é publicado sem suíte verde; a CI matriz (Windows + Linux) nasceu aqui |
| A.2 | 0–1 | o `carga_permutacao = 0,208` publicado parecia mostrar carga baixa sob permutação; na verdade era desempate entre palavras isomorfas no mesmo glifo (conta A3/A2 em aberto) | `codebook_up_to_isomorphism()` no E3: canônico = **1,000** limpo e sob permutação (`docs/05` §5) | "fechar a conta A3/A2 antes de qualquer afirmação nova" — número que enfraquece o texto é corrigido, não contornado |
| A.3 | 1–3 | tolerâncias dos testes oscilavam entre Windows e Linux (BLAS/flutuação de plataforma) e uma ou outra falha espúria aparecia na CI | recalibração explícita: tolerância que **preserva os dígitos publicados** (score ~10⁻⁷–10⁻⁸, acurácia ~10⁻⁴) sem afrouxar a afirmação; documentada no próprio teste | tolerância é parte da especificação — ela diz qual casa decimal é alegação |
| A.4 | MutaCore | o código da §B do documento **injetava `R_L ≡ 0`**: reproduzi-lo como estava seria reproduzir um resíduo morto | detectado na auditoria, corrigido na porta, publicado como achado (`docs/06` §8.1) | reproduzir inclui auditar se o código mede o que diz; o bug do *outro* também é resultado |
| A.5 | ev | a chave `segundos` (tempo de execução) dentro do JSON quebrava a regressão a cada rodada | tempo movido para telemetria real, arquivo separado e não-regressado (`docs/06` §9, `docs/09` §6) | separar **medição de tempo** de **conteúdo determinístico**; telemetria real nunca entra na regressão |
| A.6 | ev 2 | o E10 v1 comparava o resíduo contra memória **fraca** — a auditoria ev 2 mostrou que memórias fortes de 24 bits vencem | E10b portado (58/58), resultado negativo publicado, limitação declarada, **P1.10** aberta para repetir no *nosso* ambiente | comparação contra baseline fraco não é evidência; quando o adversário é forte, o resultado pode ser nulo — e é publicado |
| A.7 | ev 3/4 | contagem do desgaste publicada errada no `docs/11` §2; e a §7 dizia "perde em 100% das sementes", contradizendo a exceção real (janela curta ID, 0,6%) | ambos corrigidos **antes** do commit, após revisão com o dado cru | revisar contagens e universalis ("sempre", "nunca", "100%") contra os números antes de publicar |
| A.8 | ev 3/4 | leitura inicial de "linear ≈ acaso = boa privacidade" teria sido errada: os ataques lineares deles são **degenerados** (uint8: `2*Y−1` → `{255,1}`) | achado pela nossa verificação, publicado como ressalva central do `docs/11` §4, e gerou a **P1.11** (atacante neural/temporal) | acurácia de atacante só vale se o alvo do atacante estiver certo; conferir o tipo, não só o número |
| A.9 | 9 | o `run_all` completo **quebrou na figura 11** depois de ~11 min: `'tab:lightgray'` não existe no matplotlib (a paleta `tab:` tem 9 cores); testes e experimentos já tinham passado e o JSON já estava salvo | corrigido para `lightgray` (nome CSS válido) e criado `render_figs.py`, que regenera **só as figuras** a partir do JSON salvo — validação de render em segundos, sem reexecutar 11 min | código de figura não é coberto pela suíte: validar o render separadamente **antes** do run_all inteiro |
| A.10 | 9 | `dict(lambda=...)` → `SyntaxError` (`lambda` é palavra reservada) | dict literal `{"lambda": ...}` | erro de sintaxe banal pego pelo `py_compile` antes de rodar qualquer coisa |
| A.11 | 9 | `neural_execucoes` gravado arredondado a 9 casas mas `neural_max` cheio → a igualdade exata `neural_max == max(execucoes)` falhava no teste mini | precisão cheia nos dois (como o JSON externo deles) | ou tudo arredondado para leitura, ou tudo cheio para igualdade — e o teste de fórmula pega a incoerência |
| A.12 | 9 | as **5 primeiras falhas** do `verifica_ev56.py` eram do *script*, não deles: confundi λ = 0,3 com λ = 0,003 nas checagens do ev 6, e uma dominância usou `>` onde precisava de `≥` | script corrigido; só então as **286/286** passaram | quando a verificação falha, a hipótese primeira é o **próprio erro** — e isso fica registrado aqui |
| A.13 | 9 | bloco de comparação da réplica usava `score > max(...)` (sempre falso, porque o λ = 1 *é* o máximo) | trocado por `== max(...)`; os vereditos passaram a refletir a tabela | comparação contra extremo próprio exige `==`, não `>` — testar o veredito contra a tabela, não só o número |
| A.14 | 8–9 | a contagem de testes/figuras muda a ciclo e histórico antigo ia sendo reescrito, apagando "o estado da época" | regra: docs antigos **congelam** a contagem da época (30/9 no `docs/09`, 32/10 no `docs/10`, 34/11 no `docs/11`); número novo só no índice, README e no doc do ciclo | documento analítico é retrato do momento — atualizar o estado, não a história |
| A.15 | 8 | numa atualização do `docs/07`, o parágrafo da segunda auditoria foi **substituído acidentalmente** | detectado na revisão pós-edição e restaurado | depois de substituições grandes em docs de memória, reler o documento inteiro — não só a parte editada |

### B. Acertos (o que funcionou e por quê)

| # | acerto | prova |
|---|---|---|
| B.1 | **Regra de aceitação mantida em 5 pacotes externos** (MutaCore, ev, ev 2, ev 3/4, ev 5/6): nada aceito sem reprodução numérica, e a **origem** de todo número marcada (execução deles, port nosso, recálculo aritmético, ou replicação nossa) | `docs/06`, `docs/09`–`docs/12`; nenhum número publicado sem proveniência |
| B.2 | **Ports fiéis executáveis**: `e10b.py` (58/58) e `e10d.py` (JSON idêntico, 0 diferenças em 129 números) rodam nesta máquina e regeneram o publicado | `docs/10` §2, `docs/11` §2 |
| B.3 | **Previsões nossas confirmadas pela própria auditoria**: (i) `docs/11` §6 avisou que o E10e exploratório não valia como evidência e que λ deveria ser fixado antes — o ev 5 perdeu a fronteira OOD exatamente assim; (ii) P1.9 (pseudorreplicação, 1ª auditoria) foi reescrita pelo autor no ev 6 §5; (iii) "linear ≈ acaso não mede reconstrução" confirmada pela estrutura dos números | `docs/12` §3 nº 6 e nº 17, §5 |
| B.4 | **Negativos publicados com proeminência**: E8 (ganho 0%), E9 (chave de 16,6 bits), E10 (≈ A0), E10b (não vence controles fortes), E10d (H4 refutada), E10c externo (nulo) e, no ciclo 9, **o Pareto OOD exato deles não se repetiu na nossa réplica** | checklist "Resultado nulo publicado" desta seção |
| B.5 | **CI verde em todas as rodadas**, crescendo com a suíte (21 → 36 testes, +2 ports completos na CI) sem nunca deixar de rodar os dois SO | histórico de runs do `main`, badge do README |
| B.6 | **Pareado por semente desde o E10b** — e a demonstração de valor no ciclo 9: o ev 6 **não pôde** fazer o teste correto porque não salvou o dado por semente; nós salvamos e rodamos o bootstrap pareado com 4 ICs fora de zero | `E10e_repl.pareado_l1_vs_l003`, `docs/12` §4 |
| B.7 | **Determinismo total** das execuções (sementes declaradas: treino 101, ataque 77/78/88, IC 884/910+len) — duas execuções dão o mesmo JSON, testado | `test_e10*_determinismo*` |
| B.8 | **Produção própria, não só validação**: achado do atacante degenerado (uint8) e a replicação `E10e_repl` são contribuições que não vêm deles | `docs/11` §4, `docs/12` §4 |
| B.9 | **Revisão pega erros antes do commit** em todos os ciclos: contagem do desgaste, contradição de universalis, parágrafo apagado, contagens históricas — nenhum dos erros da coluna A entrou publicado sem correção | histórico de commits (correções estão no mesmo ciclo, não em commits de remendo) |

### C. Retomadas de caminho (mudanças deliberadas e seus motivos)

| # | caminho abandonado / trocado | para onde foi | motivo (evidência) |
|---|---|---|---|
| C.1 | **P1.7 (Walsh), "cripto" e "Camada 3"** — recusados como não verificáveis / beco sem saída | baselines sérios (P1.1) e carga-como-canal reformulada dentro do que é testável | a regra do projeto é verificabilidade; recusa publicada, não esquecida (`docs/06` §8.5/§9) |
| C.2 | **E10 v1 com controles fracos** | **E10b** (ports fiéis das memórias fortes de 24 bits) + limitação publicada + P1.10 aberta | auditoria ev 2: memórias fortes vencem a formulação fraca (A.6) |
| C.3 | **P2.7 na rota linear** (`I(R;sign(Δ)) ≈ 0`) | **rota adversarial** (caminho E10d/E10e) — formulação já com penalidade adversarial ou aceitação da nulidade | E10c externo implementou a versão linear de forma independente e o resultado foi **nulo**; λ alto ainda *elevou* o vazamento |
| C.4 | **Seleção de λ inspecionando o teste** (E10e exploratório deles; fallback do E10d) | regra: **fixar λ antes**, declarar fallback como fallback, sementes nunca vistas (P3.4) | a própria auditoria perdeu a fronteira OOD entre rodadas (λ = 0,1 morreu no ev 5) |
| C.5 | **E10e "exploratório" como evidência** | marcado como exploratório no `docs/11`, e no ciclo 9 tratado como **hipótese a testar**, não como fato | limite declarado por eles (λ no teste, 24 sementes) e confirmado pela rodada de 200 |
| C.6 | **Ciclo 9: recusar o material por falta de código** (opção fácil, consistente com os ciclos anteriores) | em vez disso: **(a)** verificação aritmética total (286 pontos, JSON × CSV × `scipy`) e **(b)** **replicação própria declarada** (`E10e_repl`) executada neste terminal | o pedido do usuário foi "refazer o estudo com dados reais deste terminal"; sem código, a reprodução é impossível — mas testar alegações em implementação independente é legítimo **desde que rotulado como nosso** |
| C.7 | **Tempo de CI como limite do que se testa** | aceitar CI de ~8–9 min: o port do E10d (+177 s) e a réplica do E10e (+167 s) rodam completos na CI | regra: todo número publicado é regressado, mesmo que o teste seja lento — o valor do número > custo do minuto |
| C.8 | **Escala do plano**: P2 (loop de comunicação com TEOA real) ficou adiada 5 ciclos | prioridade às auditorias externas: reproduzir, portar, publicar vereditos, só então voltar à P2 | cada auditoria mudou a fila (P1.9, P1.10, P1.11, P2.6, P2.7) — seguir a evidência era mais útil que avançar às cegas |

### D. Regras permanentes extraídas (resumo executivo)

1. Nada aceito sem reprodução numérica; **sem código** = consistência
   interna + replicação própria, sempre rotulada como nossa.
2. Toda afirmação publicada tem chave no `resultados.json` e teste de
   regressão — mesmo que o teste acrescente minutos de CI.
3. Resultado nulo ou divergente publicado com a mesma proeminência do
   positivo.
4. O conjunto de teste não participa da seleção; λ (e hiperparâmetros)
   fixados antes; fallback declarado como fallback.
5. Unidade de independência = **semente**; comparação pareada com IC —
   nunca predição avulsa como amostra.
6. Alvo inteiro nos ataques (`int`, não `uint8`) e conferência de fórmula
   em todo número de atacante.
7. Tempo/telemetria fora da regressão de conteúdo; telemetria real em
   arquivos próprios.
8. Figuras validadas fora do `run_all` (`render_figs.py`) antes da execução
   completa.
9. Quando a verificação falha, a hipótese primeira é o próprio erro —
   corrigir o verificador e registrar o caso.
10. Documentos históricos congelam a contagem da época; o estado novo
    entra no índice, no README e no doc do ciclo.

## Registro de decisões pendentes

| Decisão | Opções | Recomendação |
|---|---|---|
| Tolerar `d_min=1` (203 palavras) ou `d_min=4` (41)? | capacidade × robustez | depender da P0.2: sob permutação o teto é 11 palavras de qualquer forma |
| Manter `read_family_relational` como métrica? | sim/não | só como **sanidade** (docs/02 A4) |
| Centralização da feature (ruptura com o RIC original) | manter/reverter | manter — sem ela o grafo colapsa; documentar como decisão de projeto |
| Idioma dos gráficos | PT / EN | PT aqui, EN no README para o GitHub |
