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
| Experimentos | **E1–E10 + E10b** (E1–E4 núcleo, E5 resíduo, E6 agência, E7–E9 verificação externa MutaCore, **E10** paridade de orçamento — auditoria MUTARIC ev, **E10b** controles fortes de memória — auditoria MUTARIC ev 2) |
| Testes | **32/32** (`python tests/test_smoke.py`), regressão dos números publicados |
| CI | GitHub Actions, matriz **Windows + Linux** (`.github/workflows/ci.yml`, P0.5) |
| Figuras | 10 em `figs/` (geradas, determinísticas — o diff deve ser vazio ao regerar) |
| Resultados | `resultados/resultados.json` — fonte única de todos os números citados |
| Coleta real | `resultados/maquina.json` + `resultados/telemetria_real.json` — informação desta máquina, **não regressada** (`--telemetria`, `docs/09` §6) |
| Documentos | `docs/00` a `docs/10` (índice, arquitetura, achados, ponte, plano, resíduo/agência, MutaCore, continuidade, histórico, **auditoria MUTARIC ev**, **auditoria MUTARIC ev 2**) |
| Estado do texto | **protótipo exploratório**: números descritivos, sem IC nem teste de hipótese |

## 2. Retomar em 10 minutos

```bash
git clone https://github.com/ebiossanto/IA-RESEARCH-MUTARIC.git
cd IA-RESEARCH-MUTARIC
pip install -r requirements.txt

python run_all.py --so-testes    # 32 testes, segundos — faz isto PRIMEIRO
python run_all.py                # testes + E1-E10 + E10b + figuras (alguns minutos)
python -m ricemotions.experimentos --telemetria   # coleta REAL da máquina (opcional,
                                                  # requer psutil; grava arquivos próprios)
```

Se os **32 testes** passam, o trabalho está exatamente como foi publicado.
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

## 4. Próximo passo (em ordem)

A fila completa e detalhada está em `docs/04` (P1, P2, P3), com critério de aceite
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

## 5. Pendências que vivem fora deste repositório

| pendency | onde | o que fazer quando chegar |
|---|---|---|
| Repositório **PIXEL** (RIC original) | `docs/03` §5 — `Desktop/PIXEL` vazio, sem repo na conta | preencher a URL e revisar as 4 correspondências (feature, τ, `d_I`, "1 grafo único") |
| `teoa/core.py` de verdade | `Desktop/Emoções/` | P2.1: adaptador `estado → (6,32)` e repetir E1–E4 |
| Documento `MUTACORE _ RIC.md` | fora do repo (anexo do usuário) | já analisado integralmente em `docs/06`; só reabrir se houver código novo anexado |
| Documento `MUTARIC ev.md` | fora do repo (anexo do usuário) | já analisado integralmente em `docs/09` (5 correções + E10 + coleta); só reabrir se houver nova versão |
| Documento `MUTARIC ev 2.md` + `e10b.py` | fora do repo (pasta `mutaric b/MUTARIC_E10b/` no Desktop) | já analisado e reproduzido em `docs/10` (E10b portado, 58/58); só reabrir se chegar o `e10.py`/os testes deles, que ficaram **não verificáveis** |
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
--so-testes` → 32/32), and what is already decided and must not be reopened
without numerical reproduction. Repository:
`github.com/ebiossanto/IA-RESEARCH-MUTARIC` (public, branch `main`), CI on
Windows + Linux. Experiments are now **E1–E10 + E10b**; the external audit
"MUTARIC ev" was verified claim by claim in `docs/09` (five corrections
adopted, E10 built, real telemetry from this machine collected into
non-regressed files), and the second audit "MUTARIC ev 2" in `docs/10`
(its `e10b.py` run here with 58/58 numbers reproduced and ported as E10b:
**the residue does not beat strong memories of equal budget** — refutation
published with the same prominence). The next
concrete step is still **P1.1** (serious baselines with bootstrap CIs), then
P1.2 (paired hypothesis test) and P1.3 (perceptual transformations); P0.1–P0.5
are closed. External pendencies live outside this repo: the PIXEL repository
(`docs/03` §5) and the real `teoa/core.py` (P2.1). Section 6 is a step-by-step
checklist for adding experiment E11 without breaking the published numbers;
section 7 lists the risks a newcomer must know.
