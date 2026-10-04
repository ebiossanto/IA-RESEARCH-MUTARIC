"""
Experimentos do trabalho EMOÇÃO COM PROCEDÊNCIA (TEOA x RIC)

E1  Três alegrias (e três tristezas): a procedência se lê nas RELAÇÕES do corpo do glifo?
    relacional (RIC) vs nível vs delta vs nível+delta; limpo e sob transformações da imagem.
E2  Família afetiva: canal de NÍVEL (faixa de intensidade) vs canal RELACIONAL (par de linhas).
E3  Carga explícita: capacidade x robustez (d_min), permutação de vértices, mensagem em vários glifos.
E4  Pipeline completo (família por polaridade + procedência por relações) vs linhas de base.
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ricemotions.mundo import CLASSES, CAUSAS, FAMILIAS, make_set, affect, VARS
from ricemotions import glifo as G

# Windows grava em cp1252 por padrão e as chaves do JSON contêm "σ"; sem isto,
# main() estoura UnicodeEncodeError logo após calcular tudo.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# raiz do projeto: <raiz>/ricemotions/experimentos.py -> <raiz>
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(RAIZ, "figs")
RES = os.path.join(RAIZ, "resultados")
FAM_OF = np.array([0 if c[0] == "alegria" else 1 for c in CLASSES])
CAU_OF = np.array([CAUSAS.index(c[1]) for c in CLASSES])
D_CARGA = 4


def build(n_per_class, seed, parts):
    """Gera episódios + glifos. Devolve também os episódios (fonte da valência),
    para não precisar regenerar o conjunto só para conferir a consistência."""
    eps, y = make_set(n_per_class, seed)
    rng = np.random.default_rng(seed + 777)
    imgs, sym = [], []
    for e, k in zip(eps, y):
        v, a = affect(e)
        s = int(rng.integers(len(parts)))
        imgs.append(G.render(e, v, a, CLASSES[k][0], parts[s], rng)); sym.append(s)
    return np.array(imgs), y, np.array(sym), np.array(eps)


def graphs(imgs, tau): return np.array([G.body_graph(i, tau) for i in imgs])


def feats(imgs, kind): return np.array([G.level_feats(i, kind) for i in imgs])


def masked_alphabet_pred(Gt, A, lab, fam_pred):
    out = []
    for g, f in zip(Gt, fam_pred):
        d = np.abs(A - g).sum(1).astype(float)
        d[FAM_OF[lab] != f] = 1e9
        out.append(lab[int(np.argmin(d))])
    return np.array(out)


def main():
    rng = np.random.default_rng(0)
    os.makedirs(FIG, exist_ok=True); os.makedirs(RES, exist_ok=True)
    parts, bits = G.codebook(D_CARGA)
    Itr, ytr, _, _ = build(400, 1, parts)
    Iva, yva, _, _ = build(150, 2, parts)
    Ite, yte, ste, Ete = build(300, 3, parts)
    res = {"n_train": int(len(ytr)), "n_val": int(len(yva)), "n_test": int(len(yte)),
           "carga": dict(d_min=D_CARGA, palavras=len(parts), bits=float(np.log2(len(parts))))}

    # consistência do mundo (usa os MESMOS episódios do conjunto de teste)
    A = np.array([affect(e)[0] for e in Ete])
    res["consistencia_familia_vs_valencia"] = float(np.mean((A > 0) == (FAM_OF[yte] == 0)))

    # ---- escolha de tau na validação (nunca no teste) ----
    sweep = {}
    for tau in [0.4, 0.5, 0.6, 0.7, 0.8]:
        Gt, Gv = graphs(Itr, tau), graphs(Iva, tau)
        Aa, lab = G.alphabet(Gt, ytr)
        sweep[str(tau)] = dict(acc6=G.balanced_acc(G.decode_body_alphabet(Gv, Aa, lab), yva), grafos=int(len(Aa)))
    tau = float(max(sweep, key=lambda t: sweep[t]["acc6"]))
    res["varredura_tau_validacao"] = sweep; res["tau"] = tau

    Gtr = graphs(Itr, tau); Aa, lab = G.alphabet(Gtr, ytr)
    protos = np.stack([(Gtr[ytr == k].mean(0) > 0.5).astype(np.int8) for k in range(6)])
    lda = {k: G.LDA().fit(feats(Itr, k), ytr) for k in ["nivel", "delta", "nivel+delta"]}
    lda_fam = {f: {k: G.LDA().fit(feats(Itr[FAM_OF[ytr] == f], k), CAU_OF[ytr[FAM_OF[ytr] == f]])
                   for k in ["nivel", "delta", "nivel+delta"]} for f in (0, 1)}

    def evaluate(imgs, y, sym):
        Gt = graphs(imgs, tau); famT = FAM_OF[y]
        out = {}
        # 6 classes
        out["6c_relacional"] = G.balanced_acc(G.decode_body_alphabet(Gt, Aa, lab), y)
        for k in lda: out[f"6c_{k}"] = G.balanced_acc(lda[k].predict(feats(imgs, k)), y)
        # procedência dada a família verdadeira (3 vias)
        pred_c = masked_alphabet_pred(Gt, Aa, lab, famT)
        out["3c_relacional"] = float(np.mean(CAU_OF[pred_c] == CAU_OF[y]))
        for k in lda:
            ok = []
            for f in (0, 1):
                m = famT == f
                ok.append(np.mean(lda_fam[f][k].predict(feats(imgs[m], k)) == CAU_OF[y[m]]))
            out[f"3c_{k}"] = float(np.mean(ok))
        # E2: família
        out["fam_nivel"] = float(np.mean([G.read_family_level(i) for i in imgs] == famT))
        out["fam_polaridade"] = float(np.mean([G.read_family_relational(i) for i in imgs] == famT))
        # E4: pipeline completo
        fp = np.array([G.read_family_relational(i) for i in imgs])
        out["pipeline_completo"] = G.balanced_acc(masked_alphabet_pred(Gt, Aa, lab, fp), y)
        # E3: carga
        out["carga_acc"] = float(np.mean([G.decode_payload(i, bits, parts) == s for i, s in zip(imgs, sym)]))
        return out

    T_ = {
        "limpo": lambda I: I,
        "ruído σ=0.05": lambda I: np.array([G.t_noise(i, 0.05, rng) for i in I]),
        "ruído σ=0.10": lambda I: np.array([G.t_noise(i, 0.10, rng) for i in I]),
        "ruído σ=0.20": lambda I: np.array([G.t_noise(i, 0.20, rng) for i in I]),
        "brilho ×0.7 +0.1": lambda I: np.array([G.t_bright(i, 0.7, 0.1) for i in I]),
        "descalibração por linha": lambda I: np.array([G.t_miscal(i, rng) for i in I]),
        "desfoque temporal": lambda I: np.array([G.t_blur(i) for i in I]),
    }
    res["transformacoes"] = {k: evaluate(f(Ite), yte, ste) for k, f in T_.items()}

    # ---- permutação de vértices (a 'rotação'): subconjunto de 300 glifos ----
    sub = rng.choice(len(yte), 300, replace=False)
    Isub, ysub = Ite[sub], yte[sub]
    perm = {}
    for nome, keep, decs in [("E,T fixas (âncoras)", (0, 1), [("padrão", None), ("âncoras (24 perm.)", G.ANCHOR_PERMS), ("canonicalizado (720)", G.ALL_PERMS)]),
                             ("permutação total", (), [("padrão", None), ("canonicalizado (720)", G.ALL_PERMS)])]:
        Ip = np.array([G.t_perm(i, rng, keep) for i in Isub]); Gp = graphs(Ip, tau)
        d = {}
        for dn, pm in decs:
            d["relacional/" + dn] = G.balanced_acc(G.decode_body_alphabet(Gp, protos, np.arange(6), pm), ysub)
        for k in ["nivel", "delta"]:
            d[k + "/padrão"] = G.balanced_acc(lda[k].predict(feats(Ip, k)), ysub)
        perm[nome] = d
    res["permutacao_corpo"] = perm

    # ---- E3: carga, capacidade x robustez ----
    carga = {}
    for dm in [1, 2, 4, 6, 8]:
        pr, bt = G.codebook(dm); row = {"palavras": len(pr), "bits": float(np.log2(len(pr)))}
        r2 = np.random.default_rng(5); items = []
        for _ in range(300):
            k = int(r2.integers(6)); e = make_set(1, int(r2.integers(1e6)))[0][k]
            v, a = affect(e); s = int(r2.integers(len(pr)))
            items.append((G.render(e, v, a, CLASSES[k][0], pr[s], r2), s))
        for sg in [0.0, 0.1, 0.2, 0.3, 0.4]:
            row[f"σ={sg}"] = float(np.mean([G.decode_payload(G.t_noise(i, sg, r2), bt, pr) == s for i, s in items]))
        row["miscal"] = float(np.mean([G.decode_payload(G.t_miscal(i, r2), bt, pr) == s for i, s in items]))
        row["brilho"] = float(np.mean([G.decode_payload(G.t_bright(i, 0.7, 0.1), bt, pr) == s for i, s in items]))
        carga[f"d_min={dm}"] = row
    res["carga_capacidade"] = carga
    # carga sob permutação: padrão vs canonicalizado
    pr, bt = G.codebook(D_CARGA)
    ok_std, ok_can = [], []
    for i, s in list(zip(Ite[sub[:120]], ste[sub[:120]])):
        ip = G.t_perm(i, rng, ())
        ok_std.append(G.decode_payload(ip, bt, pr) == s)
        ok_can.append(G.decode_payload(ip, bt, pr, G.ALL_PERMS) == s)
    res["carga_permutacao"] = dict(padrao=float(np.mean(ok_std)), canonicalizado=float(np.mean(ok_can)),
                                    classes_de_isomorfismo=11, bits_max_canonicalizado=float(np.log2(11)))

    # ---- demonstração: mensagem de texto em vários glifos emocionais ----
    msg = "Ganhei!"
    base = len(parts); dig = G.text_to_digits(msg, base)
    r3 = np.random.default_rng(9); demo = dict(mensagem=msg, glifos=len(dig), base=base)
    for sg in [0.0, 0.2, 0.3]:
        rec, fams_ok = [], []
        for n, d in enumerate(dig):
            k = n % 6; e = make_set(1, 100 + n)[0][k]; v, a = affect(e)
            img = G.t_noise(G.render(e, v, a, CLASSES[k][0], parts[d], r3), sg, r3)
            rec.append(G.decode_payload(img, bits, parts)); fams_ok.append(G.read_family_relational(img) == FAM_OF[k])
        demo[f"σ={sg}"] = dict(texto=G.digits_to_text(rec, base), simbolos_certos=int(np.sum(np.array(rec) == np.array(dig))),
                               familia_certa=float(np.mean(fams_ok)))
    res["demo_mensagem"] = demo

    with open(os.path.join(RES, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    figuras(res, Ite, yte, Gtr, ytr, tau)
    print(json.dumps({k: v for k, v in res.items() if k not in ("varredura_tau_validacao",)}, indent=1, ensure_ascii=False))


def figuras(res, Ite, yte, Gtr, ytr, tau):
    # 1) galeria de glifos
    fig, ax = plt.subplots(2, 3, figsize=(10, 9))
    for k, (f, c) in enumerate(CLASSES):
        a = ax[k // 3, k % 3]; img = Ite[np.where(yte == k)[0][0]]
        a.imshow(img, cmap="gray", vmin=0, vmax=1, aspect="auto", interpolation="nearest")
        for edge in [6 - 0.5, 12 - 0.5, 30 - 0.5]: a.axhline(edge, color="red", lw=0.6)
        a.set_title(f"{f} por {c}", fontsize=10); a.set_xticks([]); a.set_yticks([3, 9, 21, 39])
        a.set_yticklabels(["nível", "polar.", "corpo", "carga"], fontsize=7)
    fig.suptitle("Glifos emocionais (pixels): níveis | polaridade | corpo E,T,C,B,G,N | carga", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "glifos.png"), dpi=130); plt.close(fig)
    # 2) grafos protótipo
    fig, ax = plt.subplots(1, 6, figsize=(15, 2.8)); m = G.NP; n = len(VARS)
    for k, (f, c) in enumerate(CLASSES):
        P = (Gtr[ytr == k].mean(0) > 0.5).astype(int)
        M = np.zeros((n, n)); M[G.IU] = P[:m]; M[(G.IU[1], G.IU[0])] = P[:m]
        M2 = np.zeros((n, n)); M2[G.IU] = P[m:]; M2[(G.IU[1], G.IU[0])] = P[m:]
        ax[k].imshow(M - M2, cmap="coolwarm", vmin=-1, vmax=1); ax[k].set_title(f"{f}\n{c}", fontsize=9)
        ax[k].set_xticks(range(n)); ax[k].set_xticklabels(VARS, fontsize=7); ax[k].set_yticks(range(n))
        ax[k].set_yticklabels(VARS if k == 0 else [], fontsize=7)
    fig.suptitle(f"Grafos protótipo do corpo (τ={tau}; vermelho +, azul −)", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "grafos_prototipo.png"), dpi=130); plt.close(fig)
    # 3) robustez E1
    names = list(res["transformacoes"]); keys = ["3c_relacional", "3c_nivel", "3c_delta", "3c_nivel+delta"]
    fig, ax = plt.subplots(1, 2, figsize=(14, 4)); w = 0.2
    for j, k in enumerate(keys):
        ax[0].bar(np.arange(len(names)) + (j - 1.5) * w, [res["transformacoes"][n][k] for n in names], w, label=k[3:])
    ax[0].axhline(1 / 3, ls=":", c="k"); ax[0].set_xticks(range(len(names))); ax[0].set_xticklabels(names, rotation=25, ha="right", fontsize=8)
    ax[0].set_title("Procedência dada a família (3 vias; acaso 0,33)"); ax[0].legend(fontsize=8)
    for j, k in enumerate(["fam_nivel", "fam_polaridade", "carga_acc"]):
        ax[1].bar(np.arange(len(names)) + (j - 1) * 0.27, [res["transformacoes"][n][k] for n in names], 0.27,
                  label={"fam_nivel": "família: nível", "fam_polaridade": "família: polaridade", "carga_acc": "carga (símbolo)"}[k])
    ax[1].set_xticks(range(len(names))); ax[1].set_xticklabels(names, rotation=25, ha="right", fontsize=8)
    ax[1].set_title("Família afetiva e carga explícita"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "robustez.png"), dpi=130); plt.close(fig)
    # 4) capacidade x robustez
    cc = res["carga_capacidade"]; sg = ["σ=0.0", "σ=0.1", "σ=0.2", "σ=0.3", "σ=0.4"]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for k, v in cc.items(): ax.plot([0, .1, .2, .3, .4], [v[s] for s in sg], "o-", label=f"{k} ({v['bits']:.1f} bits)")
    ax.set_xlabel("ruído de pixel σ"); ax.set_ylabel("símbolo decodificado"); ax.legend(fontsize=8); ax.grid(alpha=.3)
    ax.set_title("Carga explícita: capacidade × robustez")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "carga.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
