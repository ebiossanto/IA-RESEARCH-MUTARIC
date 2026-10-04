# 03 — A ponte: projeto PIXEL (RIC) × projeto TEOA

Este documento explica **o que este pacote está tentando relacionar**, o que já foi
relacionado e o que ainda não está ligado. É o ponto de partida para continuar o
desenvolvimento sem reescrever a motivação.

---

## 1. Os dois polos

| | **TEOA** | **PIXEL / RIC** |
|---|---|---|
| O que é | Teoria do Estado Ótimo Artificial: a emoção como estado diante de um **alvo** `s*` | Código de **incidência relacional** lido em **pixels**: a informação está nas *relações* entre linhas, não nos valores |
| Onde vive | `Desktop/Emoções/` (`teoa/core.py`, `docs/02_TEOA_v0_2_especificacao.md`) | repositório GitHub — **link a confirmar** (ver §5) |
| Objeto central | dinâmica `(E,T,C)`, regimes, **valência ancorada** (`nível −D` + `taxa L`), histerese, gosto × desejo | feature **centralizada** → cosseno = correlação → aresta se `|cos| > τ` → decodificação por menor **distância de incidência** `d_I` |
| Pergunta | *quando* e *por que* uma emoção surge e persiste | *o que* se pode recuperar de um estado escrito em pixels |

**ricemotions** é o terceiro elemento: recebe o estado do TEOA, escreve-o em pixels
e tenta lê-lo de volta pelo RIC.

## 2. Correspondência implementada

| Conceito TEOA | Em `ricemotions` | Onde aparece no glifo |
|---|---|---|
| estado `X(t)` dos canais | `mundo.episode()` → `(6,32)` | linhas 4-9 (CORPO) |
| distância ao alvo `D(t)` | `mundo.dist(X)` | — (só dentro de `affect`) |
| valência `v = β·L − α·(D_post − d_ref)` | `mundo.affect()` → `v` | linhas 0-1, intensidade |
| ativação (variação de `D`) | `mundo.affect()` → `act` | linha 1 |
| família (aproximação/afastamento) | `fam ∈ {alegria, tristeza}` | linhas 2-3, **polaridade** (par de linhas iguais/invertidas) |
| procedência da mudança (meta/vínculo/estado) | `cause` | reconhecida nas RELAÇÕES do CORPO |
| conteúdo proposicional / "opinião" | `payload_labels` (partição em blocos) | linhas 10-15 (CARGA) |
| RIC: correlação entre features | `glifo.corr()` (média-zero, cosseno) | — |
| RIC: aresta por limiar | `body_graph(img, τ)`, `payload_graph` | — |
| RIC: decodificação por `d_I` | `decode_body_alphabet`, `decode_payload` (Hamming) | — |
| RIC: rotação/permutação de vértices | `t_perm`, `ALL_PERMS`, `ANCHOR_PERMS` | — |

**Ruptura documentada em relação ao RIC original:** aqui a feature é **centrada** antes
do cosseno. Sem a centralização todo sinal positivo correlaciona com todo sinal
positivo e o grafo colapsa no "1 grafo único" da Fase 1 do RIC. Isso está declarado
no próprio `glifo.py` (docstring) — é uma mudança de projeto, não um detalhe.

## 3. O que já está de fato conectado

1. **A valência do TEOA vira um canal de intensidade do glifo** (linhas 0-1), e a
   família vira um canal relacional (par de linhas iguais/invertidas) — dois modos
   *distintos* de codificar a mesma dicotomia, comparáveis no E2.
2. **A procedência do TEOA é o alvo do E1**: o que se pergunta é se ela aparece
   *nas relações* entre os canais e não nos valores absolutos.
3. **A carga explícita (RIC: símbolo = grafo-alvo) coexiste** com o estado tácito no
   mesmo glifo: 5,36 bits de mensagem por glifo, canonicamente 3,46 bits sob
   permutação.

## 4. O que **não** está conectado (as lacunas reais)

| # | Lacuna | Consequência |
|---|---|---|
| L1 | `teoa/core.py` **não é usado**: `mundo.py` reimplementa um TEOA roteirizado de 6 canais, sem os regimes com histerese nem a valência ancorada | os experimentos testam o **código de leitura**, não a teoria |
| L2 | ~~Não há agente~~ → **parcial** (`docs/05` §6): existe `agente.py` com transição real, política de pesos e alvo `S*` que muda com o que foi lido. Falta: **custo/recompensa** e **valência vinda da dinâmica** (ainda sai de `affect()`) | a emoção deixou de ser só registro: o estado altera a **regra** (critério mede 0,00615 vs 0,00000). Continua sem *escolha de ação* |
| L3 | ~~Não há feedback~~ → **parcial** (`docs/05` §3-§4): quem lê **a si mesmo** altera `S*`, `w` e `τ` do próprio próximo passo. Falta: um **segundo** agente lendo e mudando (contágio, consequência da comunicação) | há feedback de leitura sobre as regras, mas ainda não sobre *outro* agente |
| L4 | **Sem memória entre glifos**: cada episódio é independente; o TEOA tem ciclos e histerese | não dá para estudar persistência/fadiga |
| L5 | **Sem faixa de neutro**: `v > 0` é a fronteira (25/1800 erros, ver docs/02 A7) | família binária forçada perto de `v≈0` |
| L6 | O leitor RIC **relê o que o escritor gravou literalmente** (linhas 4-9 = episódio `X`) | "a procedência está nas relações" é verdadeiro, mas é reconhecimento de roteiro (docs/02 A6) |
| L7 | repositório **PIXEL não localizado** para conferir correspondências detalhadas | §5 |

Nenhuma lacuna acima é bug de código: são **escopo**. Estão refletidas no plano
(`04_plano_desenvolvimento.md`).

## 5. Pendência: repositório PIXEL

A pasta local `Desktop/PIXEL` está vazia e não há repositório chamado "pixel" na
conta `github.com/ebiossanto`. Quando o link estiver disponível, preencher aqui:

```
Repositório:  <URL>
Fases/RIC:    <fase 1, fase 2, ...>
Correspondências a revisar:
  - definição original de feature (aqui: linha de patch centralizada)
  - τ original (aqui: 0,7 escolhido na validação)
  - d_I original (aqui: Hamming sobre bits de aresta)
  - "1 grafo único" da Fase 1 (aqui: evitado pela centralização)
```

## 6. Perguntas que a ponte deveria responder

1. **Q1** — a procedência é recuperável só das *relações*, ou qualquer codificação
   por nível basta? *(E1 responde hoje: `nivel+delta` = 1,000 — a hipótese
   relacional, tal como está, não é necessária.)*
2. **Q2** — o glifo sobrevive a um canal imperfeito de verdade (pixeis perdidos,
   JPEG, corte, escala)? *(hoje só há ruído gaussiano, brilho, blur e ganho/offset.)*
3. **Q3** — um segundo agente, ao ler o glifo, muda de estado?
   *(parcial: `docs/05` mostra que o agente muda **a si mesmo** ao ler — critério
   0,00615 vs 0,00000. O segundo agente, o contágio e a consequência da comunicação
   continuam abertos.)*
4. **Q4** — o TEOA com valência **ancorada** produziria uma distribuição de glifos
   diferente da dos roteiros atuais? *(L1.)*
