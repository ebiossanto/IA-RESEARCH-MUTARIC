# 00 — Índice da documentação

Ponto de entrada do repositório. Todo o resto está em `README.md` (PT) e
`README.en.md` (EN).

| Doc | Responde | Quando ler |
|---|---|---|
| `01_arquitetura.md` | Como o código é dividido, formatos, contrato das funções, determinismo | Antes de mexer em qualquer `.py` |
| `02_analise_achados.md` | O que os números significam — e o que **não** sustentam | Antes de citar qualquer número |
| `03_relacao_pixel_teoa.md` | A ponte PIXEL/RIC × TEOA: o que está ligado e as 7 lacunas | Para entender o escopo do projeto |
| `04_plano_desenvolvimento.md` | O plano P0–P3 com critério de aceite e status | Para saber o que fazer agora |
| `05_residuo_e_agencia.md` | Resíduo de Landauer, τ como humor, agência de mão dupla (E5, E6) | Para os mecanismos novos e suas provas |
| `06_analise_mutacore.md` | Análise do documento MutaCore/RIC: 18 afirmações (8 confirmadas · 6 refutadas · 4 parciais), veredito e prova (E7–E9) | Para o ciclo de verificação externa |
| `07_continuidade.md` | **Retomada**: estado, regras decididas, próximo passo, checklist de E10 | O primeiro documento ao voltar ao projeto |
| `08_historico_completo.md` | **História**: todos os estudos feitos e todas as mudanças de direção | Para o relatório completo do trabalho |

## Ordem de leitura

- **5 minutos:** `README.md` (resultado em uma linha + limites) e este índice.
- **30 minutos:** + `04` (plano e status) e `07` (como retomar).
- **2 horas:** + `02` (achados e limitações), `06` (provas do ciclo MutaCore),
  `05` (mecanismos), `01` (contrato), `03` (ponte), `08` (histórico).

## Onde vivem as coisas

```
ricemotions/     código (mundo · glifo · residuo · agente · homeostase · experimentos)
tests/           27 testes de sanidade + regressão dos números publicados
resultados/      resultados.json — fonte única dos números citados (regenerável)
figs/            8 figuras geradas (regeneráveis; o diff deve ser vazio)
.github/         CI: matriz Windows + Linux rodando os testes
```

## Convenções

1. Documentos em **português**, numerados `NN_titulo.md`; resumo em inglês ao fim
   de cada um e versão completa em `README.en.md`.
2. Todo número citado em texto vem de `resultados/resultados.json` e é
   regenerado por `python run_all.py`.
3. Nenhum número muda sem passar pelos testes e sem ser documentado.
4. Nenhuma afirmação externa é aceita sem reprodução numérica (`docs/06` §1).
