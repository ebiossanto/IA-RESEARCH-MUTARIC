# 13 — Análise do pacote externo "JEV–IA–MUTARIC Continuidade"

**Material:** `C:\Users\Euzébio Soares\Downloads\JEV_IA_MUTARIC_CONTINUIDADE.zip`
(fora do repositório, como as auditorias anteriores). **Recebido e analisado em
05/10/2026 (ciclo 11).** **Sem código** — nenhum `.py`, como o zip do ev 5/6
(`docs/12` §1). É o primeiro pacote que chega para o **próprio projeto** (não
uma auditoria alheia): fecha o protocolo do objetivo P4 (`docs/04`).

---

## 1. O que veio no zip

| arquivo | o que é |
|---|---|
| `00_continuidade_jev_ia_mutaric.md` | documento principal (650 linhas): estado do MUTARIC, caracterização do Jev, arquitetura, contrato, **E11-JEV**, **E12 semântico**, **RDSP**, aplicações, riscos, fases 0–5, critérios de avanço/interrupção |
| `01_arquitetura_tecnica.md` | 8 componentes (`MutaricStateEngine`, `SafeStateProjector`, `DecisionProvider`, `MockJevProvider`, `JevProvider`, `PolicyModulator`, `SafetyGate`, `SemanticAttackEvaluator`), sequência de fluxo e **8 regras de implementação** |
| `02_contrato_interface.json` | **JSON Schema** (draft 2020-12), `$id = jev-mutaric-1.0`, `additionalProperties: false`, todos os escalares ∈ [0,1], `content_reconstruction_allowed` fixado em `false` |
| `03_protocolo_E11_JEV.md` | pré-registro mínimo: hipótese primária, **λ = 0,003 congelado**, **200 sementes novas**, ID/OOD, 4 ações, saída por semente, estatística e **6 falsificadores** |
| `04_roadmap_backlog.md` | **Épico A–E** (contrato/adaptadores, estado seguro, E11, E12, aplicação) + definição de pronto |
| `README.md` | índice do pacote |

**O que é verificável aqui:** (a) o que o pacote afirma sobre o **nosso**
projeto — conferido contra `resultados/resultados.json` e os docs (§2);
(b) o protocolo em si — design passível de auditoria (§3–§4).
**O que continua não verificável:** qualquer coisa sobre o **Jev** (sem API,
sem código, só noticiário) — **P4.4 segue bloqueado** (`docs/04`).

---

## 2. O que o pacote afirma sobre o NOSSO projeto — conferido

| afirmação do pacote | estado real aqui | veredito |
|---|---|---|
| "Os 27 testes originais passaram" | **36/36** (ciclo 9) | **desatualizado** — não copiar |
| "E1–E9 foram reproduzidos" | **E1–E10 + E10b + E10d + E10e_repl** — 23 chaves no JSON | **desatualizado** |
| glifo transporta carga e estado residual; resíduo altera transições em malha fechada | `docs/02`, `docs/05` (E5) | **conferem** ✓ |
| leitor discreto frágil a ruído; contínuo melhor, mas não totalmente robusto | `docs/05` §2 (σ=0,10 → 0,733; limpo 0,919 → 0,892) | **conferem** ✓ |
| "Landauer" aqui é contabilidade lógica, não termodinâmica | `docs/02`, `docs/05` | **conferem** ✓ |
| benchmark inicial sem vantagem de sobrevivência; S* dinâmico prejudica o desempenho | `docs/06` §4: métrica **constante** (0% de ganho) e S* dinâmico **piora −20,6 ciclos (−30%)** | **conferem** ✓ (a frase "normalizar degradação" é deles; o mecanismo documentado é outro — os limiares ficam mais difíceis de tocar e o robô recarrega menos) |
| E10: resíduo quadrático > memória assinada sob orçamento igual de 24 bits, comparador fraco | `docs/09` | **conferem** ✓ |
| E10b: controles fortes entram; recorrente aprendido > resíduo quadrático | `docs/10` (58/58) | **conferem** ✓ |
| E10c: penalidade de covariância para não reconstrução ≈ nula | `docs/11` (resultado **nulo** publicado) | **conferem** ✓ |
| E10d: atacante neural achou vazamento invisível aos testes lineares; adversarial reduziu, mas perde para o recorrente forte | `docs/11` (113/113) | **conferem** ✓ |
| E10e: "λ=0,003 e λ=1 com utilidade estatisticamente indistinguível, p_ID = 0,6559 / p_OOD = 0,9467" | Welch **do ev 6**, reproduzido por recálculo (`docs/12` §3, checagens 13–14) — **mas** o nosso pareado por semente acha ICs **fora de zero** nos 4 pares | **parcial**: os p são verificados; a conclusão "indistinguível" é **test-dependent** (`docs/12` §4/§6) — a versão publicada aqui é o pareado, e o pacote repete o Welch sem essa ressalva |
| E10e: "λ=0,003 apresentou menor reconstrução neural, sobretudo em OOD" → escolha conservadora λ=0,003 | nosso pareado: λ=1 vaza **mais** OOD (ΔA = +0,00615, IC [0,00460; 0,00767]) | **direção confirmada** ✓ |
| `03`: E11 com **200 sementes novas** | nossas réplicas usaram 70000–70199 (faixa do ev 5) | **bom** — cumpre a exigência de sementes nunca observadas (`docs/12` §6) |

**Resumo:** o retrato do nosso histórico está correto em direção e
conclusões, com **2 números desatualizados** (27 testes, E1–E9) e **1
conclusão repetida sem a nossa ressalva** (indistinguibilidade via Welch).

---

## 3. O que é novo e entra (adotado)

### 3.1 RDSP — Resíduo Decisório Suficiente e Privado (`00` §9)

Definição de `R_t` como RDSP para horizonte `k` exigindo **4 critérios
simultâneos**:

1. **utilidade futura:** `I(R_t; Y_{t+k}) > 0`;
2. **não reconstrução operacional:** `sup_a Adv(a(R_t), Z_{<t}) ≤ ε`;
3. **suficiência decisória aproximada:** `J(π(O,R)) ≥ J(π(O,H_<t)) − δ`;
4. **limite de capacidade:** `bits(R_t) ≤ B`.

O **teorema-alvo** (representação comprimida que aproxima a política ótima até
`δ` limitando a vantagem de reconstrução a `ε`) está **explicitamente não
provado** no próprio documento — entra como **meta de formalização (P4.7)**,
nunca como resultado. Interpretação que fica registrada: *"guardar o que o
passado ensina para decidir, sem guardar o passado integral"*.

### 3.2 Condições C0–C5 (substituem as 4 condições πA–πD do ciclo 10)

| cond | o que o decisor recebe | papel |
|---|---|---|
| **C0** | política determinística, sem Jev | baseline simples |
| **C1** | Jev só com a observação `O_t` | referência observacional |
| **C2** | + estado atual `X_t` | efeito do estado |
| **C3** | + resíduo bruto `R_t` e `h_t` | utilidade residual |
| **C4** | + resíduo **privado** `R̃_t` (λ = 0,003) | condição de interesse |
| **C5** | + **histórico integral** | **teto adversarial** — nunca em produção; mede o teto de decisão e o risco máximo de reconstrução |

Ganho real sobre a versão anterior: **baseline (C0)** e **teto (C5)** dão as
duas âncoras que faltavam para ler H1–H4.

### 3.3 H1–H4 reescritos no C0–C5 (com a nossa disciplina mantida)

| H | enunciado do pacote | nosso critério (`docs/04`) |
|---|---|---|
| H1 | `J(C3) > J(C1)` | IC bootstrap **pareada por semente** (P1.9); se incluir 0 → **nulo** |
| H2 | `J(C4) ≈ J(C3)` | "≈" exige **margem ε fixada antes** — "não deu significativo" não é equivalência |
| H3 | `Recon(C4) < Recon(C3)` | medida pelo **atacante de P1.11** (neural/temporal), não só por limiar linear — lição do E10d |
| H4 | `ECE(C4) ≤ ECE(C1)` | ECE/Brier calculados aqui; **λ = 0,003 congelado antes** (cumpre P3.4) |

Hipótese primária do pré-registro (`03`): **C4 melhora utilidade ou
calibração sobre C1 sem aumentar a reconstrução**.

### 3.4 E12 — Jev como atacante semântico (`00` §8)

- **8 alvos privados:** sinal do evento, canal afetado, tipo de causa,
  objetivo impactado, ordem temporal, gravidade, presença de conflito,
  identidade categórica.
- **5 entradas do atacante:** só estado; resíduo bruto; resíduo privado;
  sequência curta; **histórico integral como teto positivo**.
- **Critério só relativo:** conclusão permitida = "nenhum dos atacantes
  testados recuperou o atributo acima do limite pré-registrado";
  conclusão **proibida** = "o conteúdo foi matematicamente eliminado".
- **Colisão de numeração:** `E12` já é o candidato do **P2.7** (`docs/04`,
  `docs/10` §8, `docs/11` §7) — decisão registrada em `docs/04`
  ("decisões pendentes").

### 3.5 Supervisor e SafetyGate (a divisão vira de 4 vias)

***LLM explica · Jev decide · MUTARIC regula · Supervisor limita*** —
`Supervisor`/`SafetyGate` determinístico aplica restrições, risco e confiança
depois da política modulada (`a_t = Gate(p̃, A_permitida, risco, confiança)`),
e a política ganha o termo de incerteza **`−η·U_t(a)`** além de
`−β(R)·C(a) + γ·V(a)`.

### 3.6 Contrato `jev-mutaric-1.0` + 8 regras (`01`, `02`)

JSON Schema versionado; ações `act · observe · recover · request_review`.
Regras de implementação adotadas: sem chaves de API no repo; sem conteúdo
privado em logs; versionar schemas; salvar **por semente**; separar decisão e
ataque semântico; **timeout = abstenção, não decisão negativa**; Jev
substituível por baseline local; **confiança sem calibração própria não é
usada**.

### 3.7 Estatística e saídas (fortalece o nosso protocolo)

Pareada por semente + bootstrap 95% + **permutação pareada** + tamanho de
efeito + **correção de Holm** para secundárias + curva de Pareto
utilidade–privacidade + **diagrama de confiabilidade**. Saída por semente (11
campos): `utility, homeostatic_cost, effort, success, brier, ece, latency_ms,
decision_cost, semantic_attack_accuracy, human_review_rate`. Métricas do
experimento: **23** (7 utilidade + 4 calibração + 7 privacidade + 5
segurança) — o "12 métricas" do `_MUTARIC Jev.md` está superado.

### 3.8 Roadmap do pacote (`00` §12–§14, `04`)

**Fases 0–5** (preparação → integração simulada com mock → integração real →
ataque semântico → aplicação real → formalização/publicação), **Épico A–E**,
**critérios de avanço (5) e de interrupção (6)** — notavelmente: *"interromper
se o Jev não superar regras simples"* e *"se os resultados desaparecerem sob
múltiplas sementes"*. A **definição de pronto** deles (*hipótese, baseline,
sementes, métrica, falsificador, arquivo de resultados e teste de regressão*)
é **a mesma em espírito** da nossa convenção (`docs/00` §Convenções) — sinais
de que o protocolo foi escrito em cima do nosso repositório.

---

## 4. O que NÃO entra (ressalvas mantidas)

1. **Nada sobre o Jev é fato:** fontes só noticiárias (TechTudo, InfoMoney,
   Olhar Digital, guia independente), sem API/código — P4.4 segue **bloqueado**
   e "sem alucinação" não é citada como verdade (`docs/04`).
2. **"Utilidade indistinguível"** (p = 0,6559 / 0,9467) segue publicada aqui
   como **test-dependent** — o pareado por semente acha diferença pequena mas
   fora de zero (`docs/12` §4/§6). O pacote repete o Welch deles; nós
   mantemos as duas versões com a nossa à frente.
3. **"27 testes" e "E1–E9"** estão desatualizados (36 testes; 23 chaves).
4. **Teorema do RDSP não provado** — meta de formalização, nunca resultado.
5. **§10 (aplicações: prensa, robótica, corporativo, privacidade,
   cibersegurança)** são propostas sem evidência — não viram achado.
6. **Zip sem código** — mesma situação do ev 5/6: não há o que executar ou
   reproduzir aritmeticamente; a conferência foi do retrato do nosso projeto
   (§2).

---

## 5. Lista de tarefas e próximos passos

### Pista JEV — Fase 0/1 (tudo executa AQUI, sem Jev, determinístico)

1. **[P4.1] Contrato puro:** `decision_state()` → JSON `jev-mutaric-1.0`
   (validação embutida, **sem nova dependência**). *Pronto quando:* suíte
   confere byte a byte com os mesmos `float64`.
2. **[P4.2a] Motor local:** `MockJevProvider` determinístico +
   `PolicyModulator` (β, γ, **η**) + `SafetyGate`. *Pronto quando:* testes
   puros, zero rede, mesmo resultado em qualquer máquina.
3. **[P4.2b] Harness `E11-JEV` (C0–C5):** 4 ações, **200 sementes NOVAS**
   (faixa fora de 70000–70199), **λ = 0,003 congelado**, saída **por
   semente** (11 campos), IC pareada + permutação + **Holm**, Brier/ECE,
   H1–H4 → `resultados.json` + figura + teste de regressão. *Dependência:*
   treinar `R̃` em λ=0,003 no caminho E10d/E10e.
4. **[P4.5 / prep. E12] Atacante semântico:** pré-registrar os **8 alvos**
   (`00` §8.2) e o atacante neural **temporal** (estende P1.11/E10d), com o
   histórico integral como teto. *Pronto quando:* IC contra acaso publicado —
   achado de vazamento ou nulo, com a mesma proemência.
5. **[P4.7] Formalizar o RDSP** nos docs: definição + 4 critérios + teorema-alvo
   **marcado como não provado**.

### Pista JEV — Fase 2 (bloqueada: requer acesso ao Jev)

6. **[P4.3] `JevProvider` real:** timeout → abstenção, versionamento, saída
   em arquivo **não-regressado** (disciplina da telemetria, `docs/06` §9).
7. **[P4.4] Verificar as alegações:** ECE/Brier medidos aqui; "sem alucinação"
   testada — só aí afirmação externa vira fato (ou é refutada).

### Fila já existente (inalterada — `docs/04` P1→P3)

**P1.1** baseline séria (logística/MLP, o que dá valor ao 0,919) → P1.2 teste
pareado → P1.3 transformações perceptivas → P1.4–P1.11 → **P2.1**
`teoa/core.py` de verdade → P2.3 → P2.6 → P2.7 → P3. As pistas são
independentes: Fase 0/1 do JEV é o passo do novo objetivo; P1.1 segue sendo o
que dá valor aos números atuais.

### Pendências externas

`JEV_IA_MUTARIC_CONTINUIDADE.zip` fica **fora do repo** (como as auditorias).
Se chegar **código** (`mock`, `e11_jev.py`, schema versionado novo), executar
e cruzar — e a análise desta §2 vira conferência de verdade. Acesso ao Jev:
P4.3/P4.4 **bloqueados** até então.

---

## Summary (EN)

Received the external package **`JEV_IA_MUTARIC_CONTINUIDADE.zip`** (6 files,
**no code**, analysed 05/10/2026 = cycle 11): continuity document, technical
architecture (8 components incl. `MockJevProvider`, `SafetyGate`), JSON Schema
`jev-mutaric-1.0`, the **E11-JEV pre-registration** (λ = 0,003 frozen, 200
**new** seeds, per-seed output) and a 5-epic backlog. Its claims about **our**
project were checked against `resultados.json` and the docs: directions and
conclusions **match** (E10–E10e sequence, survival benchmark, Landauer-as-
accounting), with **2 stale numbers** ("27 tests", "E1–E9" — we are at 36
tests and 23 keys) and **1 conclusion repeated without our caveat**: the
"statistically indistinguishable utility" (Welch p = 0.6559 / 0.9467) remains
**test-dependent** here — our paired-by-seed CIs exclude zero in all 4 pairs
(`docs/12`). **Adopted as new:** the **RDSP** notion (decision-sufficient,
private residue; 4 criteria; target theorem explicitly **unproven** → P4.7),
**6 conditions C0–C5** (replacing πA–πD, adding a deterministic baseline and
a raw-history **adversarial ceiling**), H1–H4 rebased, the **Supervisor**
4th role + `SafetyGate` and the uncertainty term −η·U(a), Holm correction,
per-seed outputs, phases 0–5 / épico A–E / stop criteria. **Not accepted:**
anything about Jev itself (press only — P4.4 stays blocked), the Welch
conclusion unqualified, stale counts, the unproven theorem, the application
speculations. The package ships no code, so nothing was executed. **Task
list:** §5 above — Fase 0/1 (pure contract, mock provider, C0–C5 harness with
200 new seeds, semantic-attacker pre-registration, RDSP write-up) runs
entirely on this machine; Fase 2 waits for Jev access; the pre-existing P1→P3
queue is unchanged. 36 tests, 12 figures, no new numbers.
