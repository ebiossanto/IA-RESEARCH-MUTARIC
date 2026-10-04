# 01 — Arquitetura e contrato do código

Este documento mapeia o pacote **ricemotions**: o que cada módulo faz, quais são as
dimensões de cada estrutura e onde os arquivos entram e saem. É a referência para
continuar o desenvolvimento sem reler o código inteiro.

---

## 1. O pipeline em uma frase

> Um **episódio** (mundo TEOA, 6 canais × 32 passos) vira **valência + ativação**,
> é **renderizado como uma imagem 48×32** e a imagem é **lida de volta** por um
> código relacional (RIC) que a converte em **grafos** e decodifica **família,
> procedência e carga**.

```
mundo.episode()          6×32  E,T,C,B,G,N  rotulado (família × procedência)
     │
mundo.affect()           valência v, ativação act        ← TEOA (níveis −D e taxa L)
     │
glifo.render()           imagem 48×32 (16 patches × 32 colunas)
     │
glifo.patches()          16×32 (média dos 3 pixels de cada patch)
     ├── linhas 0-1  NÍVEL       → read_family_level / features "nivel"
     ├── linhas 2-3  POLARIDADE  → read_family_relational
     ├── linhas 4-9  CORPO       → body_graph (30 bits) → alfabeto/procedência
     └── linhas 10-15 CARGA      → payload_graph (15 bits) → símbolo
```

## 2. Módulos

| Arquivo | Responsabilidade | Depende de |
|---|---|---|
| `ricemotions/mundo.py` | Gerar episódios e rotulá-los; valência/ativação | numpy |
| `ricemotions/glifo.py` | Escrever e ler a imagem; alfabetos; grafos; leitor contínuo; simetria canônica | numpy, scipy (hadamard), `mundo` |
| `ricemotions/residuo.py` | E5: gerar/rotear resíduo (banda, simetria), energia Landauer, τ efetivo | numpy, `mundo` |
| `ricemotions/agente.py` | E6: transição com acoplamento `J`, `modular()` (mão dupla), critério | numpy, `mundo`, `glifo`, `residuo` |
| `ricemotions/homeostase.py` | MutaCore (§B–§E): resíduo **endógeno** `ΔH_L→R_L→Φ`, telemetria→`S*`/`τ`, política, robô do benchmark | numpy, `mundo` |
| `ricemotions/experimentos.py` | E1–E10, E10b, figuras, I/O de disco | os acima, matplotlib, json |
| `tests/test_smoke.py` | Sanidade dos contratos + regressões dos números publicados (32 testes) | o pacote |
| `run_all.py` | Ponto de entrada único | subprocess |

**Regra de organização:** `mundo`, `glifo`, `residuo`, `agente` e `homeostase` não
fazem I/O; só `experimentos` escreve em disco (`figs/`, `resultados/`). Isso mantém a
simulação testável. A única exceção em `homeostase` é `telemetria()`, **opcional e
nunca usada** por teste ou experimento (leitura de hardware é não-determinística).

## 3. Formatos e invariantes

| Estrutura | Formato | Observação |
|---|---|---|
| episódio | `(6, 32)` float em `[0,1]` | ordem `E T C B G N` |
| valência `v` | float (sem cota) | `v = β·L − α·(D_post − d_ref)`, `L = D_pre − D_post` |
| ativação `act` | float em `[0,1]` | média de `|Δd|` × 12, cortada |
| glifo | `(48, 32)` em `[0,1]`, quantizado em 255 níveis | `48 = NROWS(16) × R(3)` |
| glifo com resíduo (roteamento B) | `(66, 32)` | `66 = (16 + 6) × R`; banda `SL_RES = slice(16,22)` |
| patch | `(16, 32)` | média das 3 linhas de pixels do patch |
| grafo do corpo | `(30,)` int8 | 15 pares × 2 camadas (sinal `+` e `−`) |
| grafo da carga | `(15,)` int8 | `|cos| > τ_carga` |
| aresta contínua | `c (15,)`, `w (15,)` | `body_cont(img, corrigir)` — de-atenuação + peso de confiabilidade |
| simetria | `p = (6,)` permutação | `canon_order` (média + desempate léxico); `simetria_ordem` devolve `p⁻¹` |
| alfabeto | `A (m,30)`, `lab (m,)` | grafos únicos do treino + rótulo majoritário |
| codebook da carga | `parts (n,)`, `bits (n,15)` | partições restritas + vetores de co-pertinência |
| estado do agente | `X, S*, w, res, tau, C` (6,) e escalar | `agente.Agente`; `log` registra a trajetória |

Constantes importantes (definidas no topo de `glifo.py`):
`R=3`, `NROWS=16`, `SL_NIVEL/SL_POL/SL_CORPO/SL_CARGA` (fatias de patch-linha),
`WALSH` (31 portadoras de Hadamard de média zero), `IU` (15 pares de 6 vértices),
`ALL_PARTS` (203 = Bell B₆), `ALL_PERMS` (720 = 6!), `ANCHOR_PERMS` (24 = 4!, E,T fixas).

## 4. Contrato das funções centrais

### Escrever (`glifo.py`)

```python
render(X, v, act, fam, payload_labels, rng) -> (48, 32)
    # linhas 0-1: intensidade da valência e da ativação
    # linhas 2-3: mesma portadora; iguais se alegria, invertidas se tristeza
    # linhas 4-9: o próprio episódio X (os 6 canais)
    # linhas 10-15: uma portadora por BLOCO da partição (mesmo bloco = mesma linha)
```

### Ler (`glifo.py`)

```python
patches(img)                  -> (16, 32)
corr(M)                       -> matriz de cossenos centralizados ( correlação )
body_graph(img, tau)          -> (30,)   15 pares × {>tau, <−tau}
payload_graph(img, tau=0.5)   -> (15,)   15 pares × {|cos| > tau}
read_family_relational(img)   -> 0|1     sinal do cosseno entre as 2 linhas de polaridade
read_family_level(img)        -> 0|1     média da linha de nível > 0.5
decode_payload(img, bits, parts, perms=None) -> índice do símbolo
decode_body_alphabet(G, A, lab, perms=None)  -> rótulo por menor distância de incidência
level_feats(img, kind)        -> "nivel" | "delta" | "nivel+delta"
```

### Transformações de imagem (para o E1)

`t_noise`, `t_bright`, `t_blur`, `t_miscal`, `t_perm` — todas recebem a imagem e
devolvem uma imagem; `t_perm` permuta as linhas-de-patch do CORPO (mantendo `keep`
fixo) e da CARGA sempre por inteiro.

## 5. Experimentos (`experimentos.py`)

| Experimento | Pergunta | Métrica principal |
|---|---|---|
| **E1** | a procedência se lê nas RELAÇÕES do corpo? | `3c_relacional` vs `3c_nivel/delta/nivel+delta` |
| **E2** | família por canal de nível vs canal relacional? | `fam_nivel` vs `fam_polaridade` |
| **E3** | capacidade × robustez da carga (d_min, ruído, permutação) | `carga_*`, incl. `carga_isomorfismo` |
| **E4** | pipeline completo (polaridade + relações) vs baselines | `pipeline_completo` |
| **curva σ** | quanto o limiar fixo colapsa sob ruído? | `curva_sigma` (4 leitores × 7 valores de σ) |
| **E5** | o mesmo estado residual em três codificações: espalhado / banda / simetria | `E5_residuo` (classe, carga, ordinal do resíduo) |
| **E6** | a leitura realimenta as PRÓPRRIAS regras de transição? | `E6_agencia` (mão dupla, Landauer, τ, reatividade) |
| **E7** | o resíduo do MutaCore reproduz o JSON publicado? e a previsão "nível cai, relacional segura" vale aqui? | `E7_residuo_mutacore` (dose-resposta γ=0,8/×10/×100) |
| **E8** | o benchmark de sobrevivência mede emoção? (reprodução fiel + ablação 2×2×2 + varredura) | `E8_sobrevivencia` (ciclos, limites analíticos, efeito do `S*`) |
| **E9** | a cifra cuja chave é o resíduo tem quantos bits? | `E9_chave_residuo` (espaço de chave, força bruta) |
| **E10** | com o MESMO orçamento, o resíduo supera memória convencional? (4 agentes: sem memória / ruído / conteúdo / resíduo) | `E10_orcamento` (J pareado, reconstrução do conteúdo, MI excedente) |
| **E10b** | e contra memórias **fortes** de igual orçamento (24 bits)? (EMA assinada, magnitude, janela, recorrente aprendido; ID + OOD) | `E10b_controles` (scores, Δ pareados com IC bootstrap, decodificação) |

A linha **curva σ** é um experimento à parte **sem número "E"** (é o item P0.4 do
plano, feito junto com o leitor robusto). Ou seja: são E1–E10, E10b **mais** a
curva × σ.

Análise, vereditos e provas de E7–E9: `docs/06_analise_mutacore.md`.
Do E10 e da auditoria MUTARIC ev (5 correções + coleta real da máquina): `docs/09_analise_mutaric_ev.md`.
Do E10b e da auditoria MUTARIC ev 2 (58/58 números reproduzidos, formulação forte refutada): `docs/10_analise_mutaric_ev2.md`.

Boas práticas **já** seguidas aqui (manter):

- `τ` é escolhido **na validação** (`varredura_tau_validacao`), nunca no teste.
- Treino/validação/teste vêm de **seeds distintos** (1, 2, 3).
- Baselines (`nivel`, `delta`) usam o **mesmo** conjunto de imagens.
- `balanced_acc` em todas as comparações de classe.

## 6. Entradas, saídas e determinismo

```
python run_all.py               # testes + experimentos
python run_all.py --so-testes   # só testes (segundos)
python -m ricemotions.experimentos
python tests/test_smoke.py
```

- Saídas: `figs/{glifos,grafos_prototipo,robustez,carga,curva_sigma,residuo,agencia,mutacore,e10_orcamento,e10b_controles}.png`
  e `resultados/resultados.json`.
- Coleta **real** da máquina (não determinística, fora do `run_all` e da CI;
  requer `psutil`): `python -m ricemotions.experimentos --telemetria` grava
  `resultados/maquina.json` (metadados) e `resultados/telemetria_real.json`
  (carga ao vivo + E10 com a carga real no lugar do sintético) — `docs/09` §6.
- As seeds são fixas (`0,1,2,3,5,9,777+seed`), então o JSON regenerado é
  **determinístico** para uma mesma versão de numpy/scipy — exceto
  `E9_chave_residuo.segundos`, declarado em `campos_nao_deterministicos`
  (auditoria MUTARIC ev, correção 1).
- `figs/` e `resultados/` são criados automaticamente se não existirem.

## 7. Correções aplicadas nesta organização

| Antes | Depois |
|---|---|
| pacote chamado `files ricemotions` (espaço ⇒ `python -m` impossível) | pacote `ricemotions/` importável |
| imports relativos (`from .mundo import`) que quebram em execução direta | imports absolutos (`from ricemotions.mundo import`) |
| `../figs` implícito, sem `makedirs` | `RAIZ/figs` e `RAIZ/resultados`, criados em `main()` |
| `resultados.json` gravado junto das figuras | `resultados/resultados.json` |
| consistência do mundo regenerava o conjunto de teste inteiro | usa os episódios já gerados (`build(...)` devolve `eps`) |
| código morto em `figuras()` | removido |
| nenhum teste | `tests/test_smoke.py` (**32 testes** hoje) |
| E5 usava `Ite[:300]`, mas o conjunto de teste é **ordenado por classe** (só classe 0) | amostragem estratificada 50 × 6 (`e5_residuo`) |
| `canon_order` só aceitava `(n, T)`, estourando no bloco `(n, R, T)` | aceita ambos e usa a média das 3 linhas redundantes |
| o critério de mão dupla era contaminado pela relaxação dupla de `s` | snapshots do estado interno entre as duas chamadas (`criterio_mao_dupla`) |

Os **números** dos experimentos não foram alterados por essas correções.

> **Nota de cronologia:** as três últimas linhas (E5, `canon_order`, critério de mão
> dupla) corrigem código do **segundo** ciclo (`fdf6203`), que introduziu E5/E6 —
> entraram aqui porque a tabela lista todas as correções da reorganização, feita em
> duas etapas. O detalhe de cada uma está em `docs/05` §5.3 e §7.6.

Ciclo seguinte (MutaCore): `docs/06` §8 lista as correções de **código do documento
analisado** (snippet inerte, `cpu_percent` zerado, `landauer_stress` não usado) e uma
limitação conhecida **nossa**, `glifo.text_to_digits` perde bytes nulos iniciais —
registrada em vez de corrigida às cegas, porque mudaria números já publicados.
