# 04 — Plano de desenvolvimento

Prioridades com **critério de aceite** explícito. Cada item tem um "pronto é quando…"
para não virar lista infinita. Esforço estimado para uma pessoa, com o código atual.

---

## P0 — Travar o que existe (1–2 dias)

| # | Tarefa | Pronto quando | status (04/10/2026) |
|---|---|---|---|
| P0.1 | `python run_all.py` roda limpo em Windows e Linux | testes + experimentos verdes em ambas as plataformas | **feito** — 27/27 testes |
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

**Critério de parada da P2:** se, com o agente real, `nivel+delta` continuar 1,000 e
o relacional continuar pior, a conclusão é que a hipótese relacional **não se sustenta**
— e isso deve ser escrito, não contornado.

## P3 — Publicar (contínuo)

1. `README.en.md` já existe; manter sincronizado com o PT.
2. ~~Repositório GitHub~~ **feito** — `ebiossanto/IA-RESEARCH-MUTARIC` (privado,
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
- [x] Repositório GitHub publicado (`ebiossanto/IA-RESEARCH-MUTARIC`, privado,
      `main` + CI) *(04/10/2026)*
- [ ] Números do E1–E4 com IC e teste de hipótese.
- [ ] Resultado nulo publicado com a mesma proeminência do resultado positivo.
- [ ] Um experimento com `teoa.core` de verdade (P2.1).
- [ ] Link do repo PIXEL em `docs/03` §5.
- [ ] Toda escolha feita *depois* de ver resultado, listada. *(parcial: a troca da
      métrica de reatividade está listada em `docs/05` §7.5; as escolhas de
      `k_t`, `k_tau`, `k_relax`, `β` e `J` ainda não)*

## Registro de decisões pendentes

| Decisão | Opções | Recomendação |
|---|---|---|
| Tolerar `d_min=1` (203 palavras) ou `d_min=4` (41)? | capacidade × robustez | depender da P0.2: sob permutação o teto é 11 palavras de qualquer forma |
| Manter `read_family_relational` como métrica? | sim/não | só como **sanidade** (docs/02 A4) |
| Centralização da feature (ruptura com o RIC original) | manter/reverter | manter — sem ela o grafo colapsa; documentar como decisão de projeto |
| Idioma dos gráficos | PT / EN | PT aqui, EN no README para o GitHub |
