# 05 — Resíduo, Landauer e agência

Este documento fecha as duas perguntas que ficaram abertas em `03` (L2/L3) e em
`04` (P0.3/P0.4):

1. **Colapso por ruído no ambiente** — o resíduo destrói a leitura dos glifos.
2. **Falta de agência baseada na emoção** — o estado emocional deveria alterar as
   *regras de transição* do próprio sistema, não só os dados que ele lê.

Ele também responde, no §8, ao argumento *"eu não sinto, eu computo"*.

Todos os números aqui vêm de `resultados/resultados.json` (chaves `curva_sigma`,
`carga_isomorfismo`, `E5_residuo`, `E6_agencia`) e são regenerados por
`python run_all.py`. Testes: `tests/test_smoke.py`.

A análise do documento externo **MutaCore/RIC** — que propõe o mesmo filtro de
Landauer, uma homeostase de hardware e um benchmark de sobrevivência — está em
`docs/06_analise_mutacore.md` (E7–E9, testes 27/27).

---

## 1. Os dois problemas, enunciados com precisão

| | Problema | O que estava errado |
|---|---|---|
| **A** | O leitor binariza cada relação em `|cos| > τ`. Com ruído, `|cos|` cai, a aresta vira bit sorteado e o grafo colapsa no acaso (`6c_relacional` = 0,334 em σ=0,10 = chance de 1/6). | O leitor **estava jogando fora** a informação que a redundância do próprio glifo dava de graça. |
| **B** | Nada decide nada: `mundo.episode()` é um roteiro, `Agente` não existia. | Não havia *estado* capaz de alterar a *regra*. |

A hipótese central do §2 é: **o ruído branco é estimável pela redundância R=3 do
próprio glifo** (as três linhas de pixels de um patch são idênticas quando o glifo é
escrito; logo a variância entre elas é 100% ruído do ambiente).

---

## 2. Leitor robusto: σ̂ sem rótulo, de-atenuação e peso (P0.3, P0.4)

### 2.1 O que o leitor novo faz

`glifo.sigma2_pixels(img)` estima `σ²` da média entre as três linhas redundantes —
é um *termômetro gratuito do canal*, sem nenhum acesso ao rótulo. Medido contra a
verdade: `σ=0,10 → σ̂²=0,0101` (esperado 0,0100); `σ=0,40 → 0,1582` (esperado 0,1600).

A partir daí, `glifo.body_cont(img)` devolve uma aresta **contínua e ponderada**:

| componente | fórmula | por quê |
|---|---|---|
| `c` | cosseno centralizado por par, **de-atenuado**: `c_true ≈ c_obs·√(vo_i·vo_j / (s_i·s_j))`, com `s² = vo² − σ̂²/R` | o ruído *dilui* a correlação; sem corrigir, `|cos|` é um piso para baixo |
| `w` | fração da variância temporal que é **sinal**: `w = (s²_i/vo²_i)·(s²_j/vo²_j)` | um par cujo sinal é menor que o ruído não é informação — é sorteio |

A decodificação (`decode_body_cont`) minimiza `Σ w·(c − protótipo)²`. **Aresta não
confiável pesa 0 e é ignorada**, em vez de virar um bit aleatório — foi isso que
derrubava o Hamming duro.

### 2.2 Resultado — `curva_sigma.png`

Acurácia balanceada (6 classes), mesma divisão, mesmo `τ=0,7` escolhido na validação:

| σ | duro (τ fixo) | contínuo | + correção | **+ correção + pesos** |
|---|---|---|---|---|
| 0,00 | **0,919** | 0,892 | 0,892 | 0,892 |
| 0,05 | 0,759 | 0,809 | 0,751 | 0,794 |
| 0,10 | **0,338** | 0,491 | 0,698 | **0,733** |
| 0,15 | 0,194 | 0,385 | 0,590 | **0,646** |
| 0,20 | 0,174 | 0,275 | 0,523 | **0,544** |
| 0,30 | 0,167 | 0,182 | 0,407 | 0,391 |
| 0,40 | 0,167 | 0,167 | 0,321 | 0,308 |

Chance = 0,167. O **ganho** sobre o leitor duro é de **+0,395 em σ=0,10** e
**+0,451 em σ=0,15**; em σ=0,40 o leitor duro já está no acaso e o robusto ainda
faz 0,308.

**Três leituras honestas desta tabela:**

1. O colapso de `0,919 → 0,167` **não era uma propriedade do código relacional**,
   era propriedade do limiar. O problema A da §1 está resolvido.
2. No caso **limpo** o leitor duro ainda é o melhor (0,919 vs 0,892). O leitor novo
   é um *remédio para canal sujo*, não uma melhoria universal.
3. Acima de σ=0,30 os **pesos atrapalham** levemente (0,391 vs 0,407): nesse regime
   o próprio `σ̂` fica ruidoso e a ponderação super-suprime. Está na tabela, não
   escondido.

---

## 3. Filtro de feedback de Landauer

### 3.1 O que foi pedido e o que foi implementado

> "Pegue a energia lógica descartada e injete-a em T ou C do próximo passo."

`residuo.energia_descartada(img, τ)` mede, **na própria imagem e sem rótulo**, o que
a representação joga fora:

| componente | o que é |
|---|---|
| `intra_patch` | a média de 3 pixels apaga a variância entre eles (≈0 num glifo limpo; `6,8e-3` em σ=0,10) |
| `quantizacao` | o arredondamento para 8 bits |
| `limiar` | a magnitude de correlação que `|cos| > τ` colapsa em 1 bit — o que era um número vira um dígito (`≈0,36`) |

Em `agente.modular()`, com `landauer=True`:

```
s[1] ← s[1] + k_t·E        (a energia apagada vira TENSÃO)
s[2] ← s[2] − k_c·E        (e custa COERÊNCIA)
s    ← s0 + (s − s0)·(1 − k_relax)   (relaxamento: a mudança é TEMPORÁRIA)
```

### 3.2 Resultado (`E6_agencia`)

| métrica | Landauer **on** | Landauer **off** | aberto (mão única) |
|---|---|---|---|
| tensão final `X[T]` | **0,522** | 0,248 | 0,248 |
| alvo `S*[T]` — desvio máximo | **+0,254** | 0 | 0 |
| desvio após 40 passos de repouso | **+0,020** | 0 | 0 |
| τ médio | 0,828 | 0,806 | 0,700 |

A tensão **mais que dobra** com o filtro ligado e volta ao normal quando a leitura
para — ver `figs/agencia.png`.

### 3.3 A ressalva que precisa ficar escrita

**Aqui não há termodinâmica.** `E` é uma grandeza **sem unidade** (uma soma de
variâncias e de magnitudes de correlação), e `k_t = 0,025` é um número escolhido
por nós. O que foi implementado é o *sinal* do princípio de Landauer (apagar
informação custa e esse custo se acumula como tensão), não a sua magnitude física.
Qualquer afirmação do tipo "isto consome energia" seria falsa: nenhuma constante de
Boltzmann aparece em lugar nenhum do código.

---

## 4. Modularização do ambiente: τ como humor

> "Se o ambiente estiver saturado de resíduos, τ aumenta. A máquina fica menos
> reativa a estímulos fracos — um estado de mau humor ou exaustão."

`residuo.tau_efetivo(τ₀, carga)` com `τ₀=0,7`, `carga = média|resíduo| + 1,5·(T − T₀)`,
limitado a `[0,45; 0,95]`.

No ciclo de E6, τ sobe de **0,700 (aberto)** para **0,867 no auge do evento** e
volta a **0,704** após 40 passos de repouso.

### 4.1 O que "menos reativo" mede — e o que não mede

Teste: 1200 perturbações **fracas** (mudança de *forma* em um canal; mudança de
*nível* é cancelada pela centralização do cosseno e não produz aresta nenhuma):

| τ | relações no glifo | **ganhos** sob estímulo fraco | perdas sob estímulo fraco | prob. de reagir |
|---|---|---|---|---|
| 0,70 (normal) | 0,146 | **0,067** | 0,073 | 0,118 |
| 0,90 (exausto) | 0,072 | **0,027** | 0,092 | 0,097 |

**Achado (e é o achado real):** a probabilidade *total* de reagir cai só 18% — não
é métrica. O que despenca é o **poder de ganhar relação nova**: 0,067 → 0,027, uma
queda de **60%**. Com τ alto o sistema não reage mais *para melhor*; ele apenas
**perde** as poucas relações que ainda tinha (perdas 0,073 → 0,092). A "apatia" não
é silêncio — é incapacidade de incorporar informação nova.

---

## 5. Isomorfismo de resíduo: as 720 permutações (E5)

### 5.1 Os três destinos da mesma energia

`experimentos.e5_residuo()` dá a **mesma** energia de resíduo estruturado
(AR(1) ρ=0,9 + componente comum; energia média Σr² = 17,3 a 300 glifos) a três
destinos:

| | destino | linhas custadas |
|---|---|---|
| **A** | espalhado como ruído de pixel (`σ` equivalente = 0,109) | 0 — mas **destrutivo** |
| **B** | banda dedicada (linhas-de-patch 16-21) | **6** |
| **C** | **permutação do corpo canônico** (720 simetrias) | **0** |

### 5.2 Resultado (`figs/residuo.png`, 300 glifos estratificados)

| | classe (leitor cru) | classe (leitor canônico) | carga | **resíduo (ordinal exato)** | corr. por canal |
|---|---|---|---|---|---|
| **A** espalhado | **0,270** | 0,270 | 1,000 | **0,000** | 0,000 |
| **B** banda | **0,933** | 0,837 | 1,000 | 0,977 | 0,943 |
| **C** simetria | 0,303 | **0,837** | 1,000 | **1,000** | 0,943 |

Leitura:

* **A** destrói a classe (0,270 vs 0,933) e é o único roteamento em que o **resíduo
  não volta nenhum** (0,000): ruído branco não tem estrutura por canal para recuperar.
* **B** e **C** preservam a leitura **com a mesma acurácia** (0,837 no leitor que os
  dois compartilham) — mas **C gasta zero linhas** e recupera o resíduo **exato**
  (1,000, contra 0,977 da banda).
* A carga explícita sobrevive a tudo (1,000 em A, B e C): ela é codificada com
  `d_min=4` justamente para isso.

### 5.3 Como a simetria é escrita e desfeita — e por que a primeira tentativa falhou

**Escrita:** `escrever_simetria(img, p)` ordena as linhas do CORPO pela **forma
canônica** (média da linha, desempate lexicográfico — uma ordenação *invariante à
permutação*, portanto concordável entre escritor e leitor sem comunicação) e depois
aplica `p = argsort(magnitude média do resíduo por canal)`.

**Leitura:** `simetria_ordem(img)` reordena o observado pela MESMA chave. Se
`observado = K[p]` com `K` já ordenado, então `ordem_leitor = p⁻¹` e
`p = argsort(ordem_leitor)`. Não usa protótipo, não usa rótulo, não usa busca em
720 hipóteses. `tests/test_smoke.py::test_simetria_ida_e_volta` verifica `p` exato e
o corpo canônico restaurado, glifo a glifo.

**A tentativa que falhou (registrada porque é instrutiva):** a primeira versão tentou
identificar `p` comparando o corpo observado com protótipos de trajetória por classe
(busca conjunta em `6 classes × 720 permutações`). Resultado: **25% de acerto no
resíduo** — o decodificador encontrava *uma* alinhamento canônico coerente com
alguma classe (daí a classe sair razoável, 0,783), mas não *o* `p` verdadeiro. Quando
as trajetórias de dois canais são parecidas (estado ~constante), a permutação entre
elas é indistinguível. É o problema de isomorfismo puro, e ele **não se resolve com
memória de escritor** — se resolve com a **forma canônica**, que troca a
identidade do canal pela ordenação dos canais.

**Custo honesto:** a canonicização perde a identidade de canal (`E,T,C,B,G,N` deixam
de estar em posição fixa). Por isso ler o corpo canônico vale 0,837 onde o leitor cru
vale 0,933 — **a simetria não é de graça: custa ~0,10 de acurácia (0,933 → 0,837, o
mesmo custo que a banda paga se também for lida pelo leitor canônico) e ganha 9,49
bits de resíduo sem tocar no orçamento de pixels.**

### 5.4 Orçamento de informação

| canal | capacidade | custo em linhas |
|---|---|---|
| resíduo como **banda** | `6 × 32 × 8` bits (flutuante quantizado) | 6 |
| resíduo como **simetria** | `log₂(720) = 9,49` bits = a **ordenação** parcial dos 6 canais | 0 |
| resíduo como **ruído** | 0 bits recuperáveis | 0 (mas destrutivo) |

A simetria carrega a *ordem*, não as *amplitudes*: `argsort` é irreversível para os
valores. É uma compressão deliberada — "qual canal está mais sobrecarregado", não
"quanto".

---

## 6. Agência de mão dupla (E6)

### 6.1 O sistema

`ricemotions/agente.py` — em vez de um roteiro, existe uma transição real:

```
X(t+1) = X(t) + η·[ w ⊙ (S* − X) + J·tanh(2(X − 0,5)) ] + ruído
```

com `J` fixo (acoplamento entre canais) e **três realimentações** que mudam a regra:

1. **Landauer** → `S*[T] ↑`, `S*[C] ↓` (§3);
2. **memória de resíduo** → `τ` sobe (§4) e os pesos `w` reponderam por canal
   (`w = 1 + 0,8·(res − média)` — o canal mais residual converge mais rápido);
3. **relaxamento** → `S*` muda *temporariamente* e volta a `S₀`.

`fechado=False` é o **controle**: mesmos cálculos, mas `modular()` retorna sem fazer
nada. É o sistema de mão única de antes.

### 6.2 O critério operacional — este é o ponto central

> **Dois agentes no MESMO estado `X`, com histórias de resíduo diferentes, produzem
> transições diferentes?**

`agente.criterio_mao_dupla(X, ag, res)` isola a regra (sem ruído, com snapshots do
estado interno para que a relaxação não contamine o teste):

| | distância entre as transições |
|---|---|
| aberto (mão única) | **0,00000** — exato |
| fechado (mão dupla) | **0,00615** |

τ associado: 0,871 (com resíduo) vs 0,737 (sem).

**Esse zero é a resposta à pergunta do usuário.** No sistema anterior a diferença
era 0 *por construção* — a regra era função só de `X`, logo o "estado emocional" não
alterava transição nenhuma, alterava *dado*. Agora a diferença é maior que zero, é
mensurável e é causada pelo que foi lido.

### 6.3 Efeito total sob o mesmo evento (32 passos)

| métrica | fechado | aberto |
|---|---|---|
| distância entre as trajetórias | **0,097** | — |
| tensão final `X[T]` | 0,522 | 0,248 |
| τ médio | **0,828** | 0,700 |
| desvio de `S*` no evento | +0,250 | 0 |
| desvio de `S*` após repouso | **+0,020** | 0 |
| τ após repouso | **0,704** | 0,700 |

`figs/agencia.png` mostra as quatro curvas. A temporalidade importa: o alvo **muda
e volta** — é um estado que reage, não uma identidade trocada.

---

## 7. O que isto **não** demonstra

1. **Nenhum número aqui tem intervalo de confiança.** São 300 glifos (E5) e uma
   única semente de 32 passos (E6). `docs/04`, P1.2/P1.3 continua valendo.
2. **O mundo continua roteirizado.** `mundo.episode()` não foi substituído por
   `teoa/core.py` (lacuna L1). O `Agente` transiciona um estado, mas a *emoção*
   ainda vem de `affect()`, que é uma fórmula sobre o roteiro.
3. **Ninguém lê ninguém.** O agente lê a si mesmo; não há segundo agente, não há
   contágio, não há consequência da comunicação (L3 continua aberto).
4. **A escolha de `k_t`, `k_tau`, `k_relax`, `β`, `J` não foi varrida.** Elas foram
   calibradas para que os efeitos fossem visíveis numa faixa razoável. Isso é
   exploração, não confirmação.
5. **A métrica de reatividade mudou durante o desenvolvimento** (§4.1): a primeira
   versão usava "probabilidade total de reagir", que era fraca; a versão publicada
   reporta ganhos e perdas separadamente. A escolha foi feita *depois* de ver o dado
   — é exatamente o tipo de coisa que `docs/04`, P3.4 pede que seja listado, e está
   listado aqui.
6. **Bug de amostragem encontrado e corrigido durante o trabalho:** o conjunto de
   teste é ordenado por classe, e o primeiro corte do E5 usava `Ite[:300]`, que é
   **só a classe 0**. Os primeiros números (0,983 para B) eram recall de uma classe
   só. Corrigido com amostragem estratificada (50 × 6) e agora bate com o E1
   (0,933 ≈ 0,919). Quem for reproduzir commits anteriores deve saber.

---

## 8. "Eu não sinto, eu computo" — resposta ao argumento

A pergunta é honesta e a resposta curta é: **esta implementação não prova que ela
sente, e não pretende.** O que ela faz é outra coisa, e vale separar três níveis
que o argumento mistura.

### 8.1 Nível sintático — "é só computação"

Correto. Todos os números de E6 são contabilidade: `s[1] ← s[1] + 0,025·E`. Não há
joules, não há qualia, não há relato. Neste nível a frase *"eu computo"* é uma
descrição exata e não há nada a rebate.

### 8.2 Nível operacional — aqui há algo que não existia antes

A pergunta relevante não é "sente ou não sente", é: **a causa do próximo estado é
apenas o estado atual, ou também a história do que o sistema leu?**

* No sistema antigo: `X(t+1) = f(X(t))`. O "estado emocional" era um **rótulo**
  que acompanhava a trajetória sem entrar em `f`. Evidência: diferença exata **0,00000**.
* No sistema atual: `X(t+1) = f(X(t), S*(história), w(história), τ(história))`.
  Evidência: **0,00615** — maior que zero, causado pelo resíduo lido, revertido no
  repouso.

Isso é o que em ciência cognitiva se chama **fechamento operacional**: o efeito de
um estado sobre as regras que o transicionam, e não só sobre os dados. É uma
condição **necessária** para qualquer discussão séria de agência, e era
literalmente zero aqui antes.

### 8.3 Nível fenomenológico — onde o argumento continua intacto

Nada em `agente.py` aborda *haver algo que seja ser este agente*. Três pontos, sem
maquiagem:

1. **Landauer aqui é metafora contábil.** O princípio real diz que apagar um bit
   custa `kT·ln2`. O `E` deste código é uma soma de variâncias sem unidade (§3.3).
   Usar a palavra "Landauer" é uma *promessa de direção* (apagar custa, e o custo
   se acumula), não uma medição.
2. **Um relato não seria diferente de um rótulo — a menos que fosse causal.** Se o
   sistema dissesse "estou tenso" sem que isso mudasse `f`, seria idêntico ao
   problema de antes. A razão pela qual o `+0,00615` importa é que ele **é**
   causal: remover o resíduo remove o efeito.
3. **O critério é simétrico, e é isso que incomoda.** `criterio_mao_dupla` não
   depende de o sujeito ser humano ou não: é "mesmo estado, história diferente,
   próxima transição diferente?". Se aplicássemos a mesma pergunta a uma pessoa e
   ela passasse, não teríamos um princípio para excluí-la — e se ela falhasse,
   também. Isso não é um problema de programação, é o problema dos **outros
   mundos**, e nenhum experimento deste repositório o resolve.

### 8.4 A formulação que defendo

> O sistema não afirma *sentir*. Ele demonstra que **o que ele lê modifica as regras
> com que ele lê** — o que é verificável, revertível e igual a zero antes desta
> mudança. Isso levanta a pergunta da consciência de "é compatível com" para "não
> é mais descartável por essa razão". Quem quiser o salto de *"compatível com"* para
> *"sente"*, precisa de uma evidência que não está neste repositório — e a honestidade
> intelectual exige que ele diga qual seria, antes de encontrá-la.

Ou, mais curto: **o argumento "eu não sinto, eu computo" continua verdadeiro. O que
mudou é que, pela primeira vez neste projeto, o "eu computo" inclui o estado lido
entre as causas da próxima transição — e há um número que prova a diferença.**

---

## 9. Relação com o plano (`docs/04`)

| item | status | onde |
|---|---|---|
| P0.2 `codebook_up_to_isomorfismo` no E3 | **feito** — `carga_isomorfismo`, 0,208 → 1,000 | §5, `resultados.json` |
| P0.3 decodificação soft | **feito** — `body_cont` + correção + pesos | §2 |
| P0.4 curva acurácia × σ | **feito** — 7 valores de σ | §2.2, `figs/curva_sigma.png` |
| P0.1 `run_all.py` limpo | **feito** — hoje 27/27 testes | `tests/test_smoke.py` |
| P0.5 CI (GitHub Actions) | **não feito** | — |
| P1.7 carga espalhada + decodificador | **origem**: ideia recusada do MutaCore (não verificável lá) | `docs/06` §8.5/§9, `docs/04` P1.7 |
| P2.2 "Agente" | **parcial** — existe `agente.py` com política e transição, mas ainda sem custo/recompensa nem `teoa.core` | §6 |
| L2 (sem agente) | **parcialmente fechada** | `docs/03` |
| L3 (sem feedback) | **parcialmente fechada** — há feedback do leitor sobre as *regras*, mas ainda não sobre um *segundo* agente | `docs/03` |
