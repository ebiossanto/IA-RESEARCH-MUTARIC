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


TESTES = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main():
    falhas = 0
    for t in TESTES:
        try:
            t()
            print(f"  PASSOU  {t.__name__}")
        except AssertionError as exc:
            falhas += 1
            print(f"  FALHOU  {t.__name__}: {exc}")
    print(f"\n{len(TESTES) - falhas}/{len(TESTES)} testes passaram")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
