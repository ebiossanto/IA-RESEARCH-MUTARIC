# 02 — Análise dos resultados e achados técnicos

Números de `resultados/resultados.json` (regenerado por `python run_all.py`).
Sementes fixas: treino 1, validação 2, teste 3; τ escolhido **na validação**.

**Conjuntos:** 2400 treino / 900 validação / 1800 teste · 6 classes balanceadas.
**Carga:** `d_min=4` → 41 palavras = **5,36 bits** por glifo.

> **Este documento cobre E1–E4.** Os experimentos novos (curva acurácia × σ, E5
> resíduo, E6 agência) e a resposta ao argumento *"eu não sinto, eu computo"*
> estão em `docs/05_residuo_e_agencia.md`. Os achados A2, A3 e A5 ganharam notas
> de status apontando para lá.

---

## 1. Tabela-resumo (E1–E4)

### Condição limpa

| Método | 6 classes | Procedência (3 vias) |
|---|---|---|
| **relacional (RIC)** | 0,919 | 0,986 |
| nível | 0,786 | 0,831 |
| delta | 0,977 | 0,988 |
| **nível+delta** | **1,000** | **1,000** |
| pipeline completo (polaridade + relações) | — | 0,986 |

Família: por nível 0,986 · por polaridade 1,000. Carga: 1,000. Consistência
família×valência do mundo: 0,986.

### Robustez (6 classes → procedência)

| Transformação | relacional | delta | nível+delta | carga |
|---|---|---|---|---|
| limpo | 0,919 | 0,977 | 1,000 | 1,000 |
| ruído σ=0,05 | 0,751 | 0,978 | 1,000 | 1,000 |
| ruído σ=0,10 | **0,334** | 0,973 | 1,000 | 1,000 |
| ruído σ=0,20 | **0,172** | 0,958 | 0,999 | 1,000 |
| brilho ×0,7+0,1 | **0,919** | 0,926 | 0,998 | 1,000 |
| descalibração por linha | **0,919** | 0,975 | 0,984 | 1,000 |
| desfoque temporal | 0,898 | 0,976 | 1,000 | 0,957 |

### Permutação de linhas (isomorfismo)

| Condição | relacional | nível | delta |
|---|---|---|---|
| âncoras E,T fixas / padrão | 0,345 | 0,401 | 0,599 |
| âncoras / com âncoras (24 perms.) | 0,673 | — | — |
| permutação total / padrão | 0,193 | 0,254 | 0,294 |
| permutação total / canonicalizado (720) | 0,666 | — | — |

Carga sob permutação: padrão 0,117 · "canonicalizado" 0,208 · teto teórico
`log₂(11) = 3,46 bits`.

---

## 2. Achados

### A1 — O código relacional **não** vence as baselines triviais (E1)

No teste limpo, `nivel+delta` (duas médias por canal) faz **1,000** nas 6 classes e
**1,000** na procedência, contra 0,919 / 0,986 do relacional. O RIC só ganha em
robustez **afim** (brilho e descalibração derrubam `nivel` para 0,509/0,549, enquanto
o relacional fica em 0,919 — a centralização de `corr()` elimina ganho e offset por
linha).

> **Leitura honesta:** o E1 hoje mostra que *toda* a informação de procedência está
> no próprio traço temporal do episódio, e que uma média simples já a recupera. A
> contribuição do RIC aqui é a **invariância afim**, não a acurácia.
> **Ação:** incluir `nivel+delta` como baseline obrigatória em todos os gráficos e
> declarar isso no texto do experimento.

### A2 — O código relacional **colapsa sob ruído** (E1)

Em σ=0,10 o `6c_relacional` cai para 0,334 (= chance, 1/6) enquanto `delta` fica em
0,973. Causa mecânica: `body_graph` faz **limiarização dura** em `|cos| > τ` com
τ=0,7 fixo; o ruído de pixel vira *bit-flip* praticamente aleatório, e a
decodificação por Hamming não tem correção de erro.

> **Ação (P0):** (a) decodificação "soft" — usar a correlação contínua e ponderar
> cada bit por sua margem `|cos| − τ`; (b) τ com zona morta/histerese;
> (c) reportar a curva acurácia × σ (hoje só há pontos isolados).
>
> **Fechado em `docs/05` §2** (04/10/2026): `body_cont` faz (a) com de-atenuação e
> peso de confiabilidade, e (c) virou `curva_sigma.png` com 7 valores de σ.
> Na curva nova, σ=0,10: **0,338 → 0,733** (o E1 mede 0,334 para o mesmo limiar; a
> diferença é só a semente do ruído); σ=0,40: 0,167 (= chance) → 0,308. O caso limpo
> *piora* um pouco (0,919 → 0,892) e acima de σ≈0,30 os pesos voltam a atrapalhar
> levemente — ambos reportados na tabela de `docs/05`. (b) continua aberto; hoje
> o τ do ambiente é `tau_efetivo`, sem histerese.

### A3 — **Bug**: a carga sob permutação perde por colisão de isomorfismos

`decode_payload(..., perms=ALL_PERMS)` minimiza sobre (p, q). Se **duas** palavras do
codebook são isomorfas, ambas atingem distância 0 para o mesmo glifo e o desempate é
o primeiro índice encontrado — arbitrário. Medido:

| codebook | limpo | após permutação + canonical |
|---|---|---|
| `codebook(4)` — 41 palavras | 1,000 | **0,146 – 0,208** |
| `codebook_up_to_isomorfismo(1)` — 11 palavras | 1,000 | **1,000** (verificado) |

Há exatamente **11 classes de isomorfismo** de 6 vértices (= número de partições de
6 = shapes `(6),(5,1),(4,2),(4,1,1),(3,3),(3,2,1),(3,1,1,1),(2,2,2),(2,2,1,1),
(2,1,1,1,1),(1,1,1,1,1,1)`), o que confirma o `classes_de_isomorfismo=11` gravado no
JSON e o teto `log₂(11)=3,46 bits`.

> **Correção já implementada:** `glifo.codebook_up_to_isomorfismo()` mantém no
> máximo uma palavra por shape (testada em `tests/test_smoke.py`).
> **O que falta:** rodar o E3 com ela e regenerar a curva capacidade × robustez —
> o número publicado (0,208) é *artefato*, não limite físico.
>
> **Fechado em `docs/05` §5.4** (04/10/2026): `carga_isomorfismo` roda o E3 com ela —
> **0,208 → 1,000** limpo e sob permutação. O codebook padrão tem 41 palavras mas só
> **9 shapes**; o isomórfico tem 5 palavras = **2,32 bits** sem ambiguidade. O número
> publicado 0,208 continua gravado no JSON como artefato documentado.

### A4 — A "família por polaridade" é rótulo embutido, não leitura relacional

`render()` escreve `s = +1 se alegria, −1 se tristeza` em `rows[3]`. Por isso
`fam_polaridade = 1,000` em **todas** as transformações, inclusive σ=0,20 (o canal
sobrevive porque é uma forma de onda de alta amplitude, não porque tenha sido
inferido). É um **canário** de sanidade do canal, não evidência de que a família
seja recuperável pelas relações.

> **Ação:** usar `read_family_relational` só como verificação de integridade do
> glifo; para a afirmação científica, ler família a partir do CORPO (hoje `nivel`
> dá 0,986 — esse é o número a defender).

### A5 — Canonicalizar o corpo **reduz** acurácia (0,919 → 0,666)

Com 720 permutações o minimizador passa a ter muito mais chances de achar um grafo
espúrio próximo (efeito de múltiplas comparações). Âncoras E,T fixas + 24 permutações
(0,673) ficam praticamente igual a canonicizar tudo (0,666), ou seja, **o custo vem
do tamanho da busca, não da escolha da normalização**.

> **Ação:** testar canonicalização *real* (forma canônica do grafo, uma única
> normalização) em vez de argmin sobre 720 variantes; ou fixar âncoras e reduzir a
> busca a 24.
>
> **Situação (04/10/2026):** a *forma canônica do grafo* não foi feita — `0,666`
> continua sendo o número publicado e o argmin sobre 720 continua caro e com
> múltiplas comparações. O que se fez em `docs/05` §5 foi outro: **em vez de
> buscar entre 720 variantes, ordenar as linhas do corpo por uma chave invariante
> à permutação** (média + desempate léxico), que resolve o problema *para o E5*
> sem busca nenhuma. O custo dessa leitura canônica foi medido: **0,933 → 0,837**.
> A ação original (canonizar o grafo) segue aberta.

### A6 — O "alfabeto" é um 1-NN supervisão disfarçado, e a procedência é roteiro

`alphabet()` agrupa grafos de treino e guarda o rótulo majoritário; a decodificação é
menor distância para os protótipos. Isso é um classificador 1-NN — legítimo, mas a
frase "a procedência está nas relações" precisa ser lida assim: **o mundo escreve um
roteiro por classe (`mundo.episode`), o glifo grava `X` literalmente nas linhas
4-9, e o leitor reconhece o roteiro**. Nada emerge de um agente.

Isso está declarado no aviso do próprio `mundo.py` — é uma limitação de *escopo*,
não de código, e é o ponto que separa o protótipo de um resultado sobre emoções.

### A7 — Zona morta da valência (25/1800 inconsistências)

`consistencia_familia_vs_valencia = 0,986`. Diagnóstico completo: **todas** as 25
falhas são `alegria` com `v` ligeiramente negativo (mínimo −0,075); tristeza é
100% `v < 0` em todas as classes. Por classe (300 amostras cada):

| classe | frac(v>0) | v min | v max |
|---|---|---|---|
| alegria-meta | 0,977 | −0,075 | 1,046 |
| alegria-vínculo | 0,950 | −0,042 | 0,477 |
| alegria-estado | 0,990 | −0,011 | 0,182 |
| tristeza-* | 0,000 | −1,458 | −0,133 |

> **Interpretação:** o sinal de uma valência ~0 não é definido; o TEOA precisa de
> uma **faixa de neutro** (|v| < ε ⇒ família indeterminada) em vez de `v > 0`.
> Também explica por que `fam_nivel` (limiar 0,5 na intensidade) erra 1,4%.

### A8 — Fragilidades menores (corrigidas ou registradas)

1. **Encoding do Windows** — o JSON contém `σ` e era gravado em cp1252 →
   `UnicodeEncodeError` **depois** de rodar tudo. Corrigido (`encoding="utf-8"`).
2. **Regeneração do conjunto de teste** para calcular a consistência (mesma seed,
   mas dependia de `make_set` ser determinístico e alinhado). Corrigido:
   `build()` devolve os episódios.
3. **`LDA.fit` com < 2 amostras/classe** produz `Sw=NaN` silencioso. Registrado;
   coberto por asserção no teste.
4. **Pasta com espaço** + imports relativos ⇒ o pacote não era importável e
   `python -m` era impossível. Corrigido.
5. `figuras()` tinha código morto (`for y in [6,12,36]: pass`). Removido.

---

## 3. O que está bem (manter)

- Separação mundo ↔ glifo ↔ experimentos, sem I/O fora de `experimentos`.
- τ varrido **na validação**; seeds fixas; treino/val/test separados.
- Baselines honestas e comparadas no mesmo conjunto (`balanced_acc`).
- O E3 mostra a troca certa: `d_min=1 → 7,67 bits` cai a 0,58 em σ=0,4,
  enquanto `d_min=8 → 2,58 bits` aguenta 0,93. Isso é uma lei de canal, não um
  ajuste.
- A demo da mensagem (`"Ganhei!"`, 11 glifos, base 41) decodifica **perfeitamente**
  em σ=0,3 — coerente com o E3.
- Transparência documental: `mundo.py` já avisa que as procedências são roteiros.
