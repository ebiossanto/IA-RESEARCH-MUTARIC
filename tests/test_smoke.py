"""Testes de sanidade do ricemotions — sem dependência de framework.

Rodar:
    python tests/test_smoke.py      # imprime PASSOU/FALHOU por teste
    pytest tests/                   # se pytest estiver instalado

Cobrem o *contrato* das três camadas (mundo -> glifo -> leitura) e regressões dos
números publicados em resultados/resultados.json. Não substituem os experimentos.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ricemotions import glifo as G  # noqa: E402
from ricemotions import mundo as M  # noqa: E402
from ricemotions import residuo as R  # noqa: E402
from ricemotions import agente as A  # noqa: E402
from ricemotions import homeostase as H  # noqa: E402


# ---------------- mundo ----------------
def test_mundo_formatos():
    e = M.episode("alegria", "meta", np.random.default_rng(0))
    assert e.shape == (M.NV, M.T) == (6, 32)
    assert 0.0 <= e.min() and e.max() <= 1.0
    eps, y = M.make_set(5, 11)
    assert len(eps) == 5 * len(M.CLASSES) and y.max() == len(M.CLASSES) - 1


def test_mundo_valencia_na_faixa():
    for fam in M.FAMILIAS:
        for cause in M.CAUSAS:
            v, a = M.affect(M.episode(fam, cause, np.random.default_rng(3)))
            assert isinstance(v, float)
            assert 0.0 <= a <= 1.0, (fam, cause, a)


def test_mundo_familia_x_valencia():
    """Tristeza é sempre v<0; alegria pode ter v~0 (zona morta) — ver docs/02, achado 7."""
    eps, y = M.make_set(60, 5)
    v = np.array([M.affect(e)[0] for e in eps])
    tris = np.array([M.CLASSES[k][0] for k in y]) == "tristeza"
    assert np.all(v[tris] < 0)
    assert np.mean(v[~tris] > 0) > 0.95


# ---------------- alfabeto / codebook ----------------
def test_particoes_bell():
    assert len(G.ALL_PARTS) == 203            # B_6
    assert G.ALL_BITS.shape == (203, 15)      # 15 pares de 6 vértices
    assert G.NP == 15
    assert len(G.ALL_PERMS) == 720            # 6!
    assert len(G.ANCHOR_PERMS) == 24          # 4! com E,T fixas
    assert all(list(p)[:2] == [0, 1] for p in G.ANCHOR_PERMS)


def test_codebook_regressao():
    parts, bits = G.codebook(4)
    assert len(parts) == 41 and bits.shape == (41, 15)   # resultados.json
    assert bits.min() >= 0 and bits.max() <= 1
    # d_min respeitado entre quaisquer duas palavras
    d = np.abs(bits[:, None, :] - bits[None, :, :]).sum(-1)
    assert d[np.triu_indices(len(parts), 1)].min() >= 4


def test_isomorfismo():
    assert len(G.shape_representatives()) == 11          # partições de 6 = 11
    pw, bw = G.codebook_up_to_isomorphism(1)
    assert len(pw) == 11 and bw.shape == (11, 15)        # teto log2(11) = 3,46 bits
    assert len({G.shape(p) for p in pw}) == 11           # uma palavra por classe


# ---------------- glifo: escrever ----------------
def test_render_formato():
    e = M.episode("tristeza", "vínculo", np.random.default_rng(1))
    v, a = M.affect(e)
    img = G.render(e, v, a, "tristeza", (0, 0, 1, 1, 2, 2), np.random.default_rng(2))
    assert img.shape == (G.NROWS * G.R, G.T) == (48, 32)
    assert img.min() >= 0.0 and img.max() <= 1.0
    assert np.allclose(img, np.round(img * 255) / 255.0)  # quantizado em 8 bits


# ---------------- glifo: ler ----------------
def test_leitura_formatos():
    e = M.episode("alegria", "estado", np.random.default_rng(4))
    v, a = M.affect(e)
    img = G.render(e, v, a, "alegria", (0, 1, 2, 3, 4, 5), np.random.default_rng(5))
    assert G.patches(img).shape == (G.NROWS, G.T)
    assert G.body_graph(img, 0.7).shape == (2 * G.NP,)    # camada + e camada -
    assert G.payload_graph(img).shape == (G.NP,)
    assert G.level_feats(img, "nivel+delta").shape == (2 * M.NV,)


def test_ida_e_volta_carga():
    """Glifo limpo -> símbolo, sem permutação."""
    parts, bits = G.codebook(4)
    rng = np.random.default_rng(6)
    ok = []
    for k in range(len(M.CLASSES)):
        e = M.episode(*M.CLASSES[k], np.random.default_rng(100 + k))
        v, a = M.affect(e)
        s = int(rng.integers(len(parts)))
        img = G.render(e, v, a, M.CLASSES[k][0], parts[s], rng)
        ok.append(G.decode_payload(img, bits, parts) == s)
    assert all(ok)


def test_ida_e_volta_familia():
    """Família por polaridade (canal relacional) e por nível, em glifo limpo."""
    ok_p, ok_n = [], []
    for k, (fam, cause) in enumerate(M.CLASSES):
        e = M.episode(fam, cause, np.random.default_rng(200 + k))
        v, a = M.affect(e)
        img = G.render(e, v, a, fam, (0, 0, 1, 1, 2, 2), np.random.default_rng(300 + k))
        ok_p.append(G.read_family_relational(img) == (0 if fam == "alegria" else 1))
        ok_n.append(G.read_family_level(img) == (0 if fam == "alegria" else 1))
    assert all(ok_p)
    assert sum(ok_n) >= len(ok_n) - 1        # nível é heurístico: aceita 1 falha


def test_carga_canonica_sob_permutacao():
    """Uma palavra por isomorfismo => a carga sobrevive à permutação de linhas."""
    parts, bits = G.codebook_up_to_isomorphism(1)
    rng = np.random.default_rng(7)
    ok = []
    for k in range(len(M.CLASSES)):
        e = M.episode(*M.CLASSES[k], np.random.default_rng(400 + k))
        v, a = M.affect(e)
        s = int(rng.integers(len(parts)))
        img = G.render(e, v, a, M.CLASSES[k][0], parts[s], rng)
        ip = G.t_perm(img, rng, ())
        ok.append(G.decode_payload(ip, bits, parts, G.ALL_PERMS) == s)
    assert all(ok)


def test_permutacao_tem_ancoras():
    e = M.episode("alegria", "meta", np.random.default_rng(8))
    v, a = M.affect(e)
    img = G.render(e, v, a, "alegria", (0, 0, 1, 1, 2, 2), np.random.default_rng(9))
    out = G.t_perm(img, np.random.default_rng(10), (0, 1))
    ref = img.reshape(G.NROWS, G.R, G.T)
    got = out.reshape(G.NROWS, G.R, G.T)
    assert np.allclose(ref[4:6], got[4:6])          # E,T fixas
    assert not np.allclose(ref[10:16], got[10:16])  # carga permutada


# ---------------- resíduo: roteamento (docs/05, E5) ----------------
def _glifo_exemplo(k=0, seed=1):
    e = M.episode(*M.CLASSES[k], np.random.default_rng(seed))
    v, a = M.affect(e)
    img = G.render(e, v, a, M.CLASSES[k][0], (0, 0, 1, 1, 2, 2), np.random.default_rng(seed + 1))
    return e, v, a, img


def test_banda_residuo():
    """roteamento B: a banda RESÍDUO existe, acrescenta 6 linhas e é lida sem perda."""
    e, v, a, img = _glifo_exemplo()
    r = R.gerar(rng=np.random.default_rng(13))
    # mesmo rng do glifo original => mesmos carregadores de payload
    ib = G.render(e, v, a, "alegria", (0, 0, 1, 1, 2, 2), np.random.default_rng(2),
                  residuo=R.para_banda(r))
    assert ib.shape == ((G.NROWS + 6) * G.R, G.T) == (66, 32)
    assert np.array_equal(ib[:G.NROWS * G.R], img)       # as bandas originais não mudam
    rec = R.recuperar_banda(ib)
    assert rec.shape == r.shape
    assert np.allclose(rec, r, atol=0.005)               # só o quantizador de 8 bits
    assert np.corrcoef(R.memoria(r), R.memoria(rec))[0, 1] > 0.99


def test_simetria_ida_e_volta():
    """roteamento C: o resíduo vira permutação do corpo canônico.

    p é recuperado EXATO sem protótipo nem rótulo, e o corpo canônico volta intacto —
    é o que permite ler a classe com a mesma acurácia da condição B gastando 0 linhas.
    """
    _, _, _, img = _glifo_exemplo()
    corpo_ref = G.patches(G.ler_corpo_canonico(img))[G.SL_CORPO]
    for j in range(6):
        r = R.gerar(rng=np.random.default_rng(200 + j))
        p = np.asarray(R.para_permutacao(r))
        ic = G.escrever_simetria(img, p)
        assert ic.shape == img.shape                  # ZERO linhas extras
        assert np.array_equal(G.simetria_ordem(ic), p)
        assert np.allclose(G.patches(G.ler_corpo_canonico(ic))[G.SL_CORPO], corpo_ref, atol=1e-9)


def test_energia_landauer():
    """A energia descartada existe, é medida sem rótulo e cresce com o ruído."""
    _, _, _, img = _glifo_exemplo()
    e = R.energia_descartada(img, 0.7)
    assert {"intra_patch", "quantizacao", "limiar", "total"} <= set(e)
    assert e["total"] > 0
    assert e["intra_patch"] < 1e-6                    # glifo limpo: as 3 linhas são iguais
    sujo = G.t_noise(img, 0.1, np.random.default_rng(15))
    assert R.energia_descartada(sujo, 0.7)["intra_patch"] > 1e-4


def test_tau_do_ambiente():
    """τ sobe com o resíduo (com teto) e τ alto => menos relações no glifo."""
    assert R.tau_efetivo(0.7, 0.0) == 0.7
    assert R.tau_efetivo(0.7, 0.5) > 0.7
    assert R.tau_efetivo(0.7, 5.0) <= 0.95
    _, _, _, img = _glifo_exemplo(k=2)
    frac = [float(np.mean(G.body_graph(img, t))) for t in (0.5, 0.7, 0.9)]
    assert frac[0] >= frac[1] >= frac[2]


def test_leitor_robusto_vence_o_duro():
    """σ̂ pela redundância R=3 + de-atenuação + pesos: sob ruído, muito acima do τ fixo."""
    from ricemotions.experimentos import build, graphs
    parts, _ = G.codebook(4)
    Itr, ytr, _, _ = build(30, 1, parts)
    Ite, yte, _, _ = build(10, 3, parts)
    tau = 0.7
    Aa, lab = G.alphabet(graphs(Itr, tau), ytr)
    prot = G.body_prototypes(Itr, ytr, corrigir=True)
    rng = np.random.default_rng(42)
    In = np.array([G.t_noise(i, 0.15, rng) for i in Ite])
    duro = G.balanced_acc(G.decode_body_alphabet(graphs(In, tau), Aa, lab), yte)
    C = np.array([G.body_cont(i, True)[0] for i in In])
    W = np.array([G.body_cont(i, True)[1] for i in In])
    bom = G.balanced_acc(G.decode_body_cont(C, W, prot), yte)
    assert abs(G.sigma2_pixels(In[0]) - 0.15 ** 2) < 0.006
    assert bom > duro + 0.15, (duro, bom)


# ---------------- agência (docs/05, E6) ----------------
def test_agente_mao_dupla():
    """Critério operacional: aberto dá 0 exato; fechado muda a próxima transição."""
    X = np.full(M.NV, 0.5)
    res = np.array([0.50, 0.10, 0.42, 0.06, 0.30, 0.22])
    ab = A.Agente(M.S_STAR, fechado=False, seed=1)
    fc = A.Agente(M.S_STAR, fechado=True, seed=1)
    d_ab, _, _ = A.criterio_mao_dupla(X, ab, res)
    d_fc, tau_alta, tau_nula = A.criterio_mao_dupla(X, fc, res)
    assert d_ab == 0.0                                  # roteiro: regra não depende do estado
    assert d_fc > 1e-4                                  # mão dupla: depende
    assert tau_alta > tau_nula                          # e o limiar do ambiente também


def test_agente_landauer_e_temporariedade():
    """Landauer sobe tensão e o ALVO; sem leitura, o alvo volta ao normal."""
    seq = [R.gerar(rng=np.random.default_rng(900 + t)) for t in range(20)]
    on = A.Agente(M.S_STAR, landauer=True, seed=2)
    off = A.Agente(M.S_STAR, landauer=False, seed=2)
    Xo = np.full(M.NV, 0.5); Xf = Xo.copy()
    for t in range(20):
        Xo = off.passo(Xo, seq[t]); Xf = on.passo(Xf, seq[t])
    assert Xf[1] > Xo[1] + 0.10
    assert on.s[1] > off.s[1] + 0.05
    dev = on.s[1] - M.S_STAR[1]
    assert dev > 0.05
    on.landauer = False                                # fase de repouso
    for _ in range(60):
        Xf = on.passo(Xf, np.zeros((M.NV, M.T)))
    assert abs(on.s[1] - M.S_STAR[1]) < 0.05           # temporário: relaxa


# ---------------- utilidades ----------------
def test_lda_e_metricas():
    rng = np.random.default_rng(11)
    F = np.vstack([rng.normal(+1, 0.3, (20, 12)), rng.normal(-1, 0.3, (20, 12))])
    y = np.array([0] * 20 + [1] * 20)
    lda = G.LDA().fit(F, y)
    assert G.balanced_acc(lda.predict(F), y) > 0.95
    assert G.balanced_acc(np.array([0, 1]), np.array([0, 1])) == 1.0
    assert np.isfinite(G.LDA().fit(F, y).P).all()   # Sw precisa de >= 2 amostras/classe


def test_texto_roundtrip():
    for base in (2, 41, 203):
        for msg in ("Ganhei!", "emoção", "a"):
            assert G.digits_to_text(G.text_to_digits(msg, base), base) == msg


# ---------------- MutaCore (docs/06, E7-E9) ----------------
def test_reproduz_o_json_do_mutacore():
    """O JSON publicado do R_L (γ=0,8, α_L=0,15) é reproduzido exatamente."""
    sim = H.simular_landauer()
    for k, pub in H.PUBLICADO.items():
        for campo, v in pub.items():
            assert abs(sim[k][campo] - v) < 5e-6, (k, campo, sim[k][campo], v)
    # e a MAGNITUDE: o deslocamento injetado é ~10% da amplitude do sinal do roteiro
    assert 0.015 < sim["_max_phi"] < 0.03
    assert 0.05 < sim["_max_phi"] / float(np.ptp(H.roteiro_mutacore("alegria", "meta")[1])) < 0.2


def test_homeostase_regras():
    """Telemetria -> S* e τ (MutaCore §C) e política pela distância ao S* (§D)."""
    frio = H.S_star_homeostatico(40.0, 0.0)
    quente = H.S_star_homeostatico(80.0, 1.0)
    assert np.allclose(frio, M.S_STAR)                    # sem carga, alvo publicado
    assert np.all((0.0 <= quente) & (quente <= 1.0))      # recorte em [0,1]
    assert quente[0] < frio[0] and quente[1] > frio[1]     # aceita cansaço, sobe o teto de T
    assert quente[4] < frio[4] and quente[2] < frio[2]     # resignação de meta e de coerência
    assert H.tau_carga(0.0, 0.0) == 0.0
    assert 0.0 < H.tau_carga(1.0, 1.0) <= 0.15
    X = np.array([0.6, 0.6, 0.9, 0.7, 0.8, 0.4])
    assert H.politica(X, M.S_STAR) == "DEFENSIVA"         # T 0,6 > S*_T + 0,15
    X[1] = 0.1
    assert H.politica(X, M.S_STAR) == "EXPLORATORIA"       # E 0,6: déficit 0,2 < 0,25


def test_benchmark_mutacore():
    """Nos parâmetros publicados a morte é IMPOSSÍVEL; gasto > carga (0,12) mata."""
    def roda(gasto, **cfg):
        X, vivo = M.S_STAR.copy(), True
        rs = np.random.default_rng(0)
        for t in range(1000):
            X, vivo, _, _ = H.passo_robo(X, float(rs.uniform(0.1, 0.6)),
                                         t % 50 < 15, rng=rs, gasto=gasto, **cfg)
            if not vivo:
                return t + 1, X
        return 1000, X
    afetivo = dict(dinamico=True, generosa=True, esfria=0.10)
    c, X = roda(0.015, **afetivo)                          # gasto do documento
    assert c == 1000 and X[0] > 0.0 and X[1] < 0.95        # ninguém morre (as duas mortes)
    c_sfixo, _ = roda(0.015, dinamico=False, generosa=True, esfria=0.10)
    assert c_sfixo == 1000                                 # ablação: idem
    c_letal, _ = roda(0.15, **afetivo)
    assert c_letal < 1000                                  # gasto > carga: morre
    c_letal_fixo, _ = roda(0.15, dinamico=False, generosa=True, esfria=0.10)
    assert c_letal_fixo > c_letal                          # S* dinâmico CUSTA sobrevivência


def test_chave_acoplada_ao_residuo_e_bruteforceavel():
    """A 'chave' da cifra do MutaCore tem ~1e5 valores: 16,6 bits, força bruta trivial."""
    from ricemotions import experimentos as E
    r = E.e9_chave_residuo()
    assert r["espaco_de_chave"] == 100001 and r["bits_de_chave"] < 17.0
    assert r["roundtrip_com_chave_exata"] is True
    assert abs(r["chave_recuperada"] - 0.03452) < 1e-9     # recuperada por varredura
    assert r["candidatos_testados"] <= r["espaco_de_chave"]
    assert r["simbolos"] > 0 and r["base"] == 41


def test_carga_da_maquina_sobe_o_tau():
    """Telemetria externa -> τ do RIC; sem carga, o agente continua como em E6."""
    seq = [R.gerar(rng=np.random.default_rng(500 + t)) for t in range(12)]
    X1 = np.full(M.NV, 0.5); X2 = np.full(M.NV, 0.5)
    sem, com = A.Agente(M.S_STAR, seed=3), A.Agente(M.S_STAR, seed=3)
    for t in range(12):
        X1 = sem.passo(X1, seq[t])
        X2 = com.passo(X2, seq[t], carga_hw=1.0)
    assert com.tau > sem.tau + 0.05                        # carga sobe o limiar
    assert sem.tau >= 0.7 - 1e-9                           # e sem carga não colapsa


def test_afirmacao_do_918_nao_vale_para_ruido():
    """~91,8% vale para transformações afins; para σ≤0,30 o leitor duro vai ao acaso."""
    from ricemotions.experimentos import build, graphs
    parts, _ = G.codebook(4)
    Itr, ytr, _, _ = build(30, 1, parts)
    Ite, yte, _, _ = build(10, 3, parts)
    Aa, lab = G.alphabet(graphs(Itr, 0.7), ytr)
    def acc(imgs):
        return G.balanced_acc(G.decode_body_alphabet(graphs(imgs, 0.7), Aa, lab), yte)
    limpo = acc(Ite)
    brilho = acc([G.t_bright(i, 0.7, 0.1) for i in Ite])
    ruido = acc([G.t_noise(i, 0.30, np.random.default_rng(7)) for i in Ite])
    assert limpo > 0.75 and brilho > limpo - 0.15          # afins: mantém
    assert ruido < 0.40                                    # σ=0,30: perto de 1/6 = 0,167
    assert ruido < limpo - 0.30                            # e muito abaixo do "91,8%"


# ---------------- MUTARIC ev: correções + E10 (docs/09) ----------------
def test_e9_campo_nao_determinista_declarado():
    """Correção 1 (MUTARIC ev): 'segundos' é declarado NÃO determinístico e nenhum
    teste regressa o seu valor — a regressão do E9 cobre chave, bits e roundtrip."""
    from ricemotions import experimentos as E
    r = E.e9_chave_residuo()
    assert r["campos_nao_deterministicos"] == ["segundos"]
    assert isinstance(r["segundos"], float) and r["segundos"] > 0
    assert r["bits_de_chave"] < 17.0                       # isto sim é regressado


def test_e10_orcamento():
    """E10 (MUTARIC ev §6): orçamento igual (6 floats, mesma EMA, mesma política) —
    (a) AR reconstrói MENOS conteúdo que AM; (b) MI excedente de AR > 0; (c)
    J(AR) > J(AM) nos dois regimes. E a ressalva publicada: AR ≈ A0."""
    from ricemotions import experimentos as E
    r = E.e10_orcamento()
    d = r["design"]
    assert r["deterministico"] is True
    assert d["sementes"] == 25 and d["T_passos"] == 160 and d["alpha"] == 0.15
    assert d["l2"] == 0.0 and d["l3"] == 0.0               # sem ação; custo idêntico por construção
    # (a) conteúdo apagado: a memória convencional reconstrói o conteúdo melhor
    a = r["cond_a_rmse_reconstrucao"]
    assert a["AM"] < a["AR"] and a["AM"] < a["A0"]
    # (b) predição do futuro: excedente acima do piso do viés; controle ~ 0
    b = r["cond_b_mi_excesso"]
    assert b["AR"] > 0 and b["AM"] > b["AR"]
    assert 0.0 <= b["AN"] < b["AR"]
    # (c) J: AR > AM nos dois regimes de distúrbio — números publicados
    j = r["J"]
    assert j["conteudo"]["AR"] > j["conteudo"]["AM"]
    assert j["mudanca"]["AR"] > j["mudanca"]["AM"]
    assert abs(j["conteudo"]["AR"] + 0.141122) < 1e-4
    assert abs(j["conteudo"]["AM"] + 0.149413) < 1e-4
    assert abs(j["mudanca"]["AR"] - 0.402060) < 1e-4
    assert abs(a["AM"] - 0.082692) < 1e-4
    assert abs(b["AR"] - 0.016478) < 5e-3
    # a ressalva honesta: contra A0 (nenhuma memória) a diferença é nula
    assert abs(r["comparacoes_pareadas"]["conteudo"]["AR-A0"]["media"]) < 1e-3
    assert r["condicoes"]["c_ar_maior_nos_dois_regimes"] is True
    assert "de 3 condições" in r["veredito"]


def test_maquina_e_telemetria_fora_da_regressao():
    """Coleta real desta máquina (MUTARIC ev, correções 1 e 5): em arquivos próprios,
    o de telemetria declara deterministico=False e nenhum teste regressa os valores."""
    import json
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    m = json.load(open(os.path.join(raiz, "resultados", "maquina.json"), encoding="utf-8"))
    for k in ("sistema", "arquitetura", "python", "numpy", "nucleos_logicos",
              "memoria_total_gb", "papel"):
        assert k in m and m[k], k
    t = json.load(open(os.path.join(raiz, "resultados", "telemetria_real.json"), encoding="utf-8"))
    assert t["deterministico"] is False
    assert t["amostras"] == len(t["cpu_pct"]) >= 5
    assert all(0.0 <= c <= 100.0 for c in t["cpu_pct"])
    assert t["J"]["conteudo"]["AR"] is not None
    assert t["condicoes"]["c_ar_maior_nos_dois_regimes"] is True


TESTES = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main():
    falhas = 0
    for t in TESTES:
        try:
            t()
            print(f"  PASSOU  {t.__name__}")
        except Exception as exc:                      # noqa: BLE001 - é o runner, não o teste
            falhas += 1
            print(f"  FALHOU  {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(TESTES) - falhas}/{len(TESTES)} testes passaram")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
