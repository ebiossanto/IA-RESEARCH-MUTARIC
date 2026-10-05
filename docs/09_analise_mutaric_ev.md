# 09 — Análise da auditoria externa "MUTARIC ev" (ciclo 6)

> Documento analisado: `MUTARIC ev.md` (anexo externo, recebido em 04/10/2026).
> Ele audita o repositório publicado em <https://github.com/ebiossanto/IA-RESEARCH-MUTARIC>
> (versão com 27 testes, E1–E9). Nada aqui é aceito sem reprodução numérica —
> a mesma regra de aceitação do MutaCore vale para quem nos audita.
> Estado resultante deste ciclo: **30 testes, 9 figuras, E1–E10**, arquivos de
> telemetria da máquina próprios (`resultados/maquina.json`, `resultados/telemetria_real.json`).

---

## 1. O que o documento trouxe

1. **Cinco correções** (redacionais e analíticas) ao material publicado.
2. **Uma proposição**: uma codificação "fechada" não pode ser igual ao estado
   que ela codifica — `F(X,R) ≠ F(X,R')` para dois resíduos distintos (caso
   fechado) e igualdade no caso aberto; e a afirmação de que ela está protegida
   pelos testes.
3. **Um experimento novo (E10)**: paridade de orçamento entre quatro agentes
   (A0 sem memória / AN ruído / AM memória convencional / AR resíduo MUTARIC)
   com três condições — (a) pouco conteúdo do passado, (b) informação preditiva
   do futuro, (c) `J(AR) > J(AM)`.
4. **O pedido de usar esta máquina como fonte de dados reais**, no lugar dos
   eventos sintéticos.

## 2. Verificação das alegações do documento (provas)

| alegação do documento | verificação | resultado |
|---|---|---|
| "a única diferença entre os JSONs é `E9/segundos`" | campo a campo: publicado `0,282` s; corrida da auditoria `0,297`; nossas corridas `0,281`–`0,299` (agora `0,281`). Todas as outras chaves idênticas | **confirmada** |
| "nenhum teste afirma a duração exata" | `grep segundos tests/` devolve só as 3 linhas do teste NOVO `test_e9_campo_nao_determinista_declarado` (esta análise); antes dele, zero ocorrências. O teste do E9 afirma `espaco_de_chave`, `bits<17`, `roundtrip`, `chave_recuperada`, `candidatos<=espaco`, `simbolos`, `base` — nunca `segundos` | **confirmada** |
| "a proposição `F(X,R) ≠ F(X,R')` está protegida pelos testes" | `test_agente_mao_dupla` (`tests/test_smoke.py`): aberto `d == 0.0` **exato** (a regra não lê o resíduo) e fechado `d > 1e-4`; reprodução numérica em `E6_agencia`: `criterio_mao_dupla_aberto = 0,00000` vs `criterio_mao_dupla_fechado = 0,0061545` | **confirmada** |
| "log2(720) ≈ 9,49 bits é teto combinatório, não capacidade útil" | as rotas C do E5 recuperam a *ordem* (ordinal 1,000) mas a leitura canônica cai `0,933 → 0,837` e as amplitudes não são armazenadas; o próprio `docs/05` §5.4 já dizia "a simetria carrega a ordem, não as amplitudes" — mas só o código e parte dos docs falavam como se fosse capacidade | **correção justa — adotada** |
| "E5 não usa exatamente a mesma realização energética nas três rotas" | A distribui a energia como ruído de pixel (`σ` equivalente 0,109), B guarda a série bruta em 6 linhas, C guarda só a ordenação — a origem (estado residual, Σr² médio = 17,27) é a mesma, a energia medida em cada saída não é a mesma grandeza | **correção justa — adotada** |

## 3. As cinco correções — o que foi feito

| # | correção | status | onde ficou a prova |
|---|---|---|---|
| 1 | excluir `E9/segundos` da regressão estrita | **adotada** — a chave `campos_nao_deterministicos = ["segundos"]` está dentro do próprio resultado do E9; nenhum teste regressa o valor | `experimentos.py::e9_chave_residuo`, teste `test_e9_campo_nao_determinista_declarado`, §2 acima |
| 2 | `log2(720)=9,49` é teto combinatório, não capacidade útil | **adotada** — docstrings e `docs/05` agora dizem "teto combinatório … a ordenação, não as amplitudes; empates e distribuição limitam o que se recupera" | `experimentos.py` (`e5_residuo`), `residuo.py`, `docs/05` §5.1/§5.3/§5.4 |
| 3 | "três codificações do mesmo estado residual" no lugar de "mesma energia" | **adotada** — cabeçalho do `experimentos.py`, docstring e `_suptitle` do E5 (figura regenerada), `residuo.py`, `docs/01`, `docs/05` §5.1, `docs/08` | `figs/residuo.png` regenerada (título novo) |
| 4 | pseudorreplicação: 1800 episódios de UMA semente não são 1800 independentes | **adotada como plano**: novo item **P1.9** (protocolo hierárquico `mundo → semente → episódio`, ICs com o mundo como unidade) + limitação escrita em `docs/05` §7 | `docs/04` P1.9, `docs/05` §7 item 6 |
| 5 | eventos externos sintéticos no E6 | **adotada como plano**: novo item **P2.6** (agente sem `residuo_evento` externo, exceto intervenção controlada) — e o **E10 já nasce sem evento sintético**: o resíduo é derivado dos próprios episódios do mundo; a variante real usa a carga desta máquina (§6) | `docs/04` P2.6, `docs/05` §7 item 7, `experimentos.py::_e10_fluxo` |

## 4. A proposição e como o E10 a operationaliza

O E10 implementa a pergunta central do documento: **com o MESMO orçamento, o
resíduo oferece algo que uma memória convencional não oferece?**

**Orçamento igual (garantido por construção):** cada agente guarda 6 `float64`
com a MESMA atualização exponencial (α = 0,15, a regra de `residuo.memoria_ema`),
recebe a MESMA política `w = clip(1 + 0,8·(s − média(s)), 0,3, 2)`, o MESMO
alvo `S*`, a MESMA transição (`agente.transicao`), o MESMO ruído por semente,
os MESMOS episódios (160 passos × classe em blocos de 8), as mesmas 25 sementes
e o mesmo horizonte. Custo computacional λ3 = 0 (idêntico por construção) e
ação λ2 = 0 (nenhuma variante age) — declarados nos `design` do JSON.

**Os quatro agentes** (só o sinal `s` difere):

| sigla | sinal | o que controla |
|---|---|---|
| **A0** | zero | nenhuma memória (baseline) |
| **AN** | ruído i.i.d. com (μ, σ) por canal do AR | o que qualquer modularização de mesma amplitude faz |
| **AM** | EMA do **conteúdo** (médias por canal dos episódios) | memória convencional reconstrutiva — o baseline forte |
| **AR** | EMA das **magnitudes de mudança** \|Δconteúdo\| por canal | o resíduo MUTARIC: guarda *quanto mudou*, não *o quê* |

**Dois regimes de distúrbio** (a fonte do distúrbio pode favorecer uma memória
ou outra; por isso os dois são reportados **antes** de ver o resultado):
`conteudo` (dist = 0,35·(conteúdo − 0,5)) e `mudanca` (dist = 0,35·Δconteúdo).

**As três condições** (com o que cada uma mede de fato):

- **(a) pouco conteúdo do passado** — RMSE de teste ao reconstruir os 12
  features do episódio (média e desvio por canal) a partir do sinal, com
  **split temporal 70/30** (sem vazamento). Referência `B` = desempenho da
  própria memória convencional AM: o resíduo deve reconstruir *pior*.
- **(b) informação preditiva** — `MI(s_t ; ‖carga futura‖ em t+5)` por
  histograma (5 bins), em bits, **menos o piso do viés** (a MI empírica nunca é
  < 0; o que se afirma é o excedente ao mesmo cálculo com pares embaralhados).
- **(c) `J(AR) > J(AM)`** — `J = −λ1·distância média ao alvo + λ4·fração de
  passos perto do alvo` (λ1 = 1, λ4 = 0,5, ε = 0,10). Como as sementes são as
  mesmas, a comparação é **pareada** (diferença por semente), que é a estatística
  correta — publicada em `comparacoes_pareadas`.

## 5. Resultados do E10 (`figs/e10_orcamento.png`, chave `E10_orcamento`)

### 5.1 Condições (a) e (b)

| sinal | (a) RMSE reconstrói conteúdo | (b) MI bruta (bits) | piso embaralhado | **excedente** |
|---|---|---|---|---|
| A0 (nenhuma memória) | 0,1083 | 0,0000 | 0,0000 | 0,0000 |
| AN (ruído) | 0,1084 | 0,0033 | 0,0024 | 0,0009 |
| **AM (convencional)** | **0,0827** | **0,0500** | 0,0027 | **0,0472** |
| **AR (resíduo)** | **0,1018** | **0,0189** | 0,0025 | **0,0165** |

- **(a) vale:** o resíduo reconstrói *pior* o conteúdo que a memória
  convencional (0,1018 > 0,0827) — e quase no piso do não-informado (0,1083):
  **o resíduo não é uma codificação reconstrutiva do passado.**
- **(b) vale:** excedente de AR = **+0,0165 bits** acima do piso, enquanto o
  controle de ruído fica em +0,0009 (≈0): **o resíduo carrega informação do
  futuro que o viés não explica.**

### 5.2 Condição (c): J (25 sementes, média ± dp)

| regime | A0 | AN | AM | AR |
|---|---|---|---|---|
| `conteudo` | −0,1410 ± 0,0092 | −0,1405 ± 0,0092 | −0,1494 ± 0,0078 | −0,1411 ± 0,0093 |
| `mudanca` | 0,4018 ± 0,0051 | 0,4017 ± 0,0053 | 0,3995 ± 0,0051 | 0,4021 ± 0,0053 |

Diferenças **pareadas** (mesma semente; SE = dp/√25):

| diferença | regime `conteudo` | regime `mudanca` |
|---|---|---|
| AR − AM | **+0,0083 ± 0,0034** (t ≈ 12) | **+0,0026 ± 0,0021** (t ≈ 6) |
| AR − A0 | −0,0002 ± 0,0011 (t ≈ −0,8, **nulo**) | +0,0003 ± 0,0012 (t ≈ 1,1, **nulo**) |
| AM − A0 | −0,0085 ± 0,0030 | −0,0023 ± 0,0020 |

**Veredito: 3 de 3 condições satisfeitas** — mas com a ressalva publicada no
próprio JSON: o resíduo supera a **memória convencional** (t ≈ 12 e t ≈ 6),
**não a ausência de memória** (AR ≈ A0, nulo). A memória convencional de
conteúdo, nesta tarefa, é *pior que não ter memória* (AM − A0 = −0,0085): ela
modula a postura na direção errada quando o conteúdo não é o que a política
precisa. O controle de ruído AN ≈ A0 também saiu ≈ 0, então o efeito de J não
é "qualquer modularização" — é específico do sinal.

> **Resultado nulo parcial, publicado com a mesma proeminência:** o E10 NÃO
> demonstra que o resíduo supera a ausência de memória em `J`; demonstra que,
> com orçamento igual, ele supera a memória convencional reconstrutiva sem
> conter o conteúdo que ela contém.

## 6. Coleta desta máquina (substitui os dados sintéticos)

Comando: `python -m ricemotions.experimentos --telemetria` (requer `psutil`;
**não** roda em `run_all.py` nem na CI — saída não determinística separada,
conforme a decisão `docs/06` §9 sobre manter o núcleo determinístico).

**`resultados/maquina.json`** (metadados desta máquina que produz os números):

| campo | valor |
|---|---|
| sistema / edição | Windows 10 · 10.0.19045 |
| arquitetura / processador | AMD64 · Intel64 Family 6 Model 58 Stepping 9 |
| núcleos lógicos | 4 |
| memória total / disco total | 7,69 GB / 111,22 GB |
| Python · numpy · matplotlib · psutil | 3.12.10 · 2.5.3 · 3.11.2 · 7.2.2 |

**`resultados/telemetria_real.json`** (10 amostras × 1 s, 2026-10-04T20:16:03Z):

- CPU: 18,5%–60,0% (média 33,5%); RAM: 80,3%–82,7%; carga 0,5·CPU + 0,5·RAM ∈ [0,498; 0,706];
- sensores de temperatura: nenhum exposto no Windows (`temperaturas_C = {}` —
  a ausência é registrada, não omitida).
- **Como entra no experimento:** a carga capturada é interpolada ao longo dos
  160 passos e escala a turbulência do resíduo por `0,4 + 1,2·carga`
  (fator médio ≈ 1,06) — o evento deixa de ser sintético e passa a vir do
  hardware real, `deterministico: false`.
- **Resultado da variante real:** mesmas 3 condições (3/3), `J(AR)` de
  conteúdo = −0,141127 vs −0,141122 do sintético (a carga média desta máquina
  dá fator ≈ 1,06, perto da normalização) e MI excedente de AR = 0,0144 bits.
  Os valores mudam a cada coleta por isso **nenhum teste regressa** o arquivo —
  o teste `test_maquina_e_telemetria_fora_da_regressao` só confirma o esquema e
  a marcação `deterministico: false`.

## 7. Limitações do E10 (escritas antes de qualquer generalização)

1. **Uma política para todos** (exigência do próprio documento: "mesma
   política"): `w` só escala a aproximação ao alvo pelo desvio do sinal. AM
   tem conteúdo de sobra e não o explora de outro modo — a política única é o
   que torna a comparação justa *e* o que limita AM.
2. **MI por histograma com 5 bins** e piso embaralhado único: excedentes de
   10⁻² bits são pequenos; o teste é a comparação com AN (≈0), não a magnitude.
3. **Ambiente escolhido por nós** (blocos de 8, β = 0,35, ε = 0,10, λ1..4
   declarados): sem estrutura temporal não haveria o que prever; com estrutura,
   os dois regimes cobrem as duas fontes de distúrbio plausíveis.
4. **AR ≈ A0** é um resultado nulo de primeira ordem e está publicado como tal
   (§5.2): "resíduo vence memória convencional" só se sustenta *comparado a
   AM*, não absolutamente.
5. **A carga real desta máquina (~0,55) ficou perto da normalização**, então a
   variante real validou o *canal* (hardware → experimento) mais do que gerou
   números distintos; máquinas com carga extrema produziriam outra coisa.
6. **O comparador AM é fraco** (adotada da auditoria externa
   "MUTARIC ev 2", `docs/10` §4): AM guarda a média do conteúdo, que não é a
   estatística suficiente para distúrbios de magnitude. O E10b externo
   demonstrou — com memórias fortes de igual orçamento (24 bits) — que o
   resíduo perde para a EMA de magnitude e para o estado recorrente
   aprendido, nos dois splits. A vitória `J(AR) > J(AM)` vale contra *este*
   comparador; a ressalva `AR ≈ A0` (§5.2) já apontava no mesmo sentido.
   Repetir o E10b **no nosso ambiente** é a pendência **P1.10**.

## 8. Pendências geradas por este ciclo

- **P1.9** — protocolo hierárquico `mundo → semente → episódio` para as ICs
  (correção 4; `docs/04`).
- **P2.6** — agente do E6 sem evento externo sintético (`docs/04`).
- **P1.10** — controles fortes de memória (magnitude, janela, recorrente),
  OOD e IC bootstrap pareado **dentro do E10** (auditoria `MUTARIC ev 2`,
  `docs/10`; `docs/04`).
- Próximo experimento natural: **E11** — E10 com política *aprendida* por
  agente (hoje a política única é limitação declarada, §7.1). O **E10c**
  proposto pela auditoria ev 2 ficou como **P2.7** (`docs/04`) — atualizado
  no ciclo 8 (`docs/11` §5): a versão linear foi implementada de forma
  independente pela auditoria ev 3/4 e deu **nulo**, então o P2.7 já nasce
  com penalidade adversarial.

---

## Summary (EN)

An external audit ("MUTARIC ev") was verified claim by claim: the only
nondeterministic diff in the published JSON is indeed `E9/segundos` (0.281–0.299 s
across runs), no test ever asserted it, and the closed/open proposition
`F(X,R) ≠ F(X,R')` is protected by `test_agente_mao_dupla` (exact 0.0 open vs
0.00615 closed). All five corrections were adopted: a
`campos_nao_deterministicos` marker, log2(720) reworded as a combinatorial
ceiling (not usable capacity), "three codifications of the same residual
state" replacing "same energy", plus two planned items (P1.9 hierarchical
protocol against pseudoreplication, P2.6 agent without synthetic external
events). **E10** implements equal-budget comparison of four agents (no memory /
noise / conventional content memory / MUTARIC residue; 6 float64 each, same EMA,
policy, episodes, seeds, noise): **3 of 3 conditions hold** — the residue
reconstructs less content than conventional memory (RMSE 0.1018 vs 0.0827), its
excess MI with the future is +0.0165 bits (noise control ≈ 0), and paired
J(AR) > J(AM) in both disturbance regimes (t ≈ 12 and t ≈ 6) — **but AR ≈ A0**:
the residue beats conventional memory, not the absence of memory (published as
a partial null result). Real telemetry from this machine (Windows 10, 4 cores,
7.69 GB, CPU 18.5–60.0%) is collected into separate non-regressed files and
drives the E10 residue channel through `0.4 + 1.2·load`, replacing the
synthetic input. Status: 30 tests, 9 figures, E1–E10.
