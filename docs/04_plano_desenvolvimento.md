# 04 — Plano de desenvolvimento

Prioridades com **critério de aceite** explícito. Cada item tem um "pronto é quando…"
para não virar lista infinita. Esforço estimado para uma pessoa, com o código atual.

---

## P0 — Travar o que existe (1–2 dias)

| # | Tarefa | Pronto quando |
|---|---|---|
| P0.1 | `python run_all.py` roda limpo em Windows e Linux | testes + experimentos verdes em ambas as plataformas |
| P0.2 | `codebook_up_to_isomorfismo()` entra no E3 | `carga_permutacao` mostra `canonicalizado ≈ 1,0` e a curva `bits × σ` é regenerada; JSON e figura atualizados |
| P0.3 | Decodificação **soft** do grafo (ponderar bit por `|cos| − τ`) | `6c_relacional` em σ=0,10 **> 0,6** (hoje 0,334 = chance), sem piorar o caso limpo |
| P0.4 | Curva acurácia × σ (hoje há pontos isolados) | gráfico com 6+ valores de σ para cada método |
| P0.5 | CI mínima (GitHub Actions: `pip install -r requirements.txt && python tests/test_smoke.py`) | badge verde no README |

> **Fechar a conta do A3/A2 antes de qualquer afirmação nova.** São os dois números
> que mais enfraquecem o texto hoje.

## P1 — Fazer a afirmação sobreviver a escrutínio (1–2 semanas)

| # | Tarefa | Pronto quando |
|---|---|---|
| P1.1 | Baseline séria além de médias: regressão logística/MLP sobre o episódio achatado, e sobre o glifo achatado | tabela com 4+ métodos, mesma divisão, `balanced_acc` ± IC via bootstrap |
| P1.2 | Teste de hipótese: relacional **vs** `nivel+delta` com bootstrap pareado | Δ com intervalo de confiança; se incluir 0, o resultado é declarado **nulo** |
| P1.3 | Transformações perceptivas reais: corte de linhas/colunas, redimensionar 48×32 → 24×16, JPEG/quantização espacial, oclusão de blocos | mesma tabela de robustez com as novas colunas |
| P1.4 | Faixa de neutro na valência (`|v| < ε` ⇒ família indeterminada) | `consistencia_familia_vs_valencia` reportado **com** a taxa de "indeterminado" |
| P1.5 | Fixar âncoras e reduzir a busca canônica do corpo (24 perms. ou forma canônica verdadeira) | `permutacao_corpo` recupera > 0,85 (hoje 0,666) |
| P1.6 | Documentar **graus de liberdade do pesquisador** (τ, `d_min`, janelas 8/8, `d_ref`, `α`, `β`, `noise`, distrator 30%) | lista numerada em `docs/` — mesma disciplina do TEOA `docs/05` |

## P2 — Ligar o TEOA de verdade (2–4 semanas)

Hoje `mundo.py` é um roteiro (ver `03`, L1–L6). Esta fase é o que transforma o
pacote de "leitor de glifos" em "emoção comunicada".

| # | Tarefa | Pronto quando |
|---|---|---|
| P2.1 | Trocar `mundo.episode()` por `teoa.core` (dinâmica E,T,C, regimes, histerese) com um adaptador `estado → (6,32)` | mesmos 4 experimentos rodam com o TEOA real; comparação lado a lado |
| P2.2 | **Agente**: escolhe ações, paga custo, o mundo muda; a valência sai da dinâmica e não do roteiro | existe `agente.py` com política e `resultado` = recompensa/estado final |
| P2.3 | **Loop de comunicação**: agente A escreve glifo, agente B lê e isso altera a ação de B | experimento com 2 agentes e métrica de ganho/mutual information |
| P2.4 | Memória: sequência de glifos no tempo (ciclos, histerese do TEOA) | série temporal de glifos e detecção de regime |
| P2.5 | Mix de emoções (dois episódios sobrepostos) e glifos "ambíguos" por projeto | E1–E4 rodando em classes multi-rótulo |

**Critério de parada da P2:** se, com o agente real, `nivel+delta` continuar 1,000 e
o relacional continuar pior, a conclusão é que a hipótese relacional **não se sustenta**
— e isso deve ser escrito, não contornado.

## P3 — Publicar (contínuo)

1. `README.en.md` já existe; manter sincronizado com o PT.
2. Repositório GitHub (`.gitignore` e estrutura prontos) + link do PIXEL em `docs/03` §5.
3. Figuras com erro-padrão (hoje, um ponto por condição).
4. Pré-registro das hipóteses **antes** de rodar a P1 (lição do TEOA `docs/03`/
   `docs/05`: resultados exploratórios não são evidência confirmatória).
5. Relacionar explicitamente com a literatura: affective computing com canal
   *valência × arousal*, RL homeostático, código de canal com decisão.

---

## Definição de pronto do projeto (versão 0.2)

- [ ] `run_all.py` verde em CI.
- [ ] Números do E1–E4 com IC e teste de hipótese.
- [ ] Resultado nulo publicado com a mesma proeminência do resultado positivo.
- [ ] Um experimento com `teoa.core` de verdade (P2.1).
- [ ] Link do repo PIXEL em `docs/03` §5.
- [ ] Toda escolha feita *depois* de ver resultado, listada.

## Registro de decisões pendentes

| Decisão | Opções | Recomendação |
|---|---|---|
| Tolerar `d_min=1` (203 palavras) ou `d_min=4` (41)? | capacidade × robustez | depender da P0.2: sob permutação o teto é 11 palavras de qualquer forma |
| Manter `read_family_relational` como métrica? | sim/não | só como **sanidade** (docs/02 A4) |
| Centralização da feature (ruptura com o RIC original) | manter/reverter | manter — sem ela o grafo colapsa; documentar como decisão de projeto |
| Idioma dos gráficos | PT / EN | PT aqui, EN no README para o GitHub |
