"""
Experimentos do trabalho EMOÇÃO COM PROCEDÊNCIA (TEOA x RIC)

E1  Três alegrias (e três tristezas): a procedência se lê nas RELAÇÕES do corpo do glifo?
    relacional (RIC) vs nível vs delta vs nível+delta; limpo e sob transformações da imagem.
E2  Família afetiva: canal de NÍVEL (faixa de intensidade) vs canal RELACIONAL (par de linhas).
E3  Carga explícita: capacidade x robustez (d_min), permutação de vértices, mensagem em vários glifos.
E4  Pipeline completo (família por polaridade + procedência por relações) vs linhas de base.
E5  Resíduo do ambiente: mesma energia, três destinos (espalhado | banda | simetria).
E6  Agência: Landauer -> T/C -> tau -> pesos -> transição (mão dupla vs roteiro).
    + curva acurácia x sigma do leitor robusto (correção de atenuação por redundância).
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ricemotions.mundo import (CLASSES, CAUSAS, FAMILIAS, make_set, affect, VARS,
                               S_STAR, NV, T as T_MUNDO)
from ricemotions import glifo as G
from ricemotions import residuo as R
from ricemotions import agente as A

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


# ================= curva acurácia x sigma (leitor robusto) =================
def curva_sigma(Itr, ytr, Ite, yte, tau):
    """O mesmo ruído de pixel, quatro leitores.

    ``duro``             limiar fixo em tau: o bit é sorteado quando o ruído passa do limiar.
    ``cont``             aresta contínua + protótipo médio (sem correção).
    ``cont_corrigido``   de-atenuação: c_true ≈ c_obs·sqrt(vo_i·vo_j/(s_i·s_j)).
    ``cont_ponderado``   + peso = fração da variância que é sinal (σ̂ estimado pela
                         redundância R=3 do próprio glifo — sem nenhum rótulo).
    """
    Aa, lab = G.alphabet(graphs(Itr, tau), ytr)
    pc = G.body_prototypes(Itr, ytr, corrigir=True)
    ps = G.body_prototypes(Itr, ytr, corrigir=False)
    out = {}
    for sg in [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]:
        rng = np.random.default_rng(4000 + int(round(sg * 100)))
        In = np.array([G.t_noise(i, sg, rng) for i in Ite]) if sg > 0 else Ite
        Cs = np.array([G.body_cont(i, False)[0] for i in In])
        Cc = np.array([G.body_cont(i, True)[0] for i in In])
        Wc = np.array([G.body_cont(i, True)[1] for i in In])
        ones = np.ones_like(Cs)
        out[f"{sg}"] = dict(
            duro=G.balanced_acc(G.decode_body_alphabet(graphs(In, tau), Aa, lab), yte),
            cont=G.balanced_acc(G.decode_body_cont(Cs, ones, ps), yte),
            cont_corrigido=G.balanced_acc(G.decode_body_cont(Cc, ones, pc), yte),
            cont_ponderado=G.balanced_acc(G.decode_body_cont(Cc, Wc, pc), yte),
            sigma2_medio=float(np.mean([G.sigma2_pixels(i) for i in In[:60]])),
        )
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    xs = sorted(float(k) for k in out)
    for ch, cor in [("duro", "tab:red"), ("cont", "tab:orange"),
                    ("cont_corrigido", "tab:green"), ("cont_ponderado", "tab:blue")]:
        ax[0].plot(xs, [out[f"{x}"][ch] for x in xs], "o-", color=cor, label=ch)
    ax[0].set_title("ruído de pixel: leitor duro vs contínuo")
    ax[0].axhline(1 / 6, ls=":", c="k")
    ax[0].set_xlabel("σ do ruído"); ax[0].set_ylabel("acurácia balanceada (6 classes)")
    ax[0].set_ylim(0, 1.02); ax[0].grid(alpha=.3); ax[0].legend(fontsize=8)
    ganho = [out[f"{x}"]["cont_ponderado"] - out[f"{x}"]["duro"] for x in xs]
    ax[1].bar([str(x) for x in xs], ganho, color="tab:blue")
    ax[1].axhline(0, c="k", lw=1)
    ax[1].set_title("ganho do leitor robusto sobre o leitor duro")
    ax[1].set_xlabel("σ do ruído"); ax[1].set_ylabel("Δ acurácia")
    ax[1].set_ylim(min(ganho) - 0.09, max(ganho) + 0.06)
    ax[1].grid(alpha=.3, axis="y")
    for i, g in enumerate(ganho):
        # rótulo acima da barra; para barra negativa, acima do zero (evita os ticks)
        ax[1].text(i, g + 0.012 if g >= 0 else 0.012, f"{g:+.2f}", ha="center", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "curva_sigma.png"), dpi=130); plt.close(fig)
    return out


# ================= E5: roteamento do resíduo =================
def e5_residuo(Itr, ytr, Ite, yte, ste, Ete, parts, bits, tau, n=300):
    """A MESMA energia de resíduo com três destinos.

    ``A espalhado`` vira ruído de pixel (é o modelo das E1-E4) — destrói a leitura.
    ``B banda``     linhas-de-patch 16-21 dedicadas — leitura intacta, custa 6 linhas.
    ``C simetria``  vira uma permutação do corpo canônico — leitura intacta, custa
                    ZERO linhas e carrega a ordem dos 6 canais (log2 720 = 9,49 bits).

    Métricas: acurácia da classe (leitor cru e leitor canônico), da carga, e a
    recuperação do próprio resíduo (ordinal exato + correlação por canal).
    """
    # amostra ESTRATIFICADA: o conjunto de teste é ordenado por classe, então um
    # corte sequencial mediria uma classe só (50 x 6 = 300 glifos)
    idx = np.concatenate([np.where(yte == k)[0][:max(1, n // 6)] for k in range(6)])
    # leitor CRU (o das E1-E4) e leitor CANÔNICO (necessário para desfazer a simetria)
    Aa_r, lab_r = G.alphabet(graphs(Itr, tau), ytr)
    Itr_c = np.array([G.ler_corpo_canonico(i) for i in Itr])
    Aa_c, lab_c = G.alphabet(graphs(Itr_c, tau), ytr)
    prot_c = G.body_prototypes(Itr_c, ytr, corrigir=True)

    acc = {k: {m: [] for m in ("classe_cru", "classe_canon", "classe_soft", "carga",
                               "ordinal", "corr")} for k in ("A", "B", "C")}
    linhas = {"A": 0, "B": 6, "C": 0}
    sigmas = []
    exemplos = {}
    rng = np.random.default_rng(31)

    for i in idx:
        k, s = int(yte[i]), int(ste[i])
        img = Ite[i]
        r = R.gerar(rng=rng)
        ord_true = R.ordinal_de_r(r)
        v, a = affect(Ete[i])

        noise, sg = R.para_pixels(r, seed=1000 + int(i)); sigmas.append(sg)
        ia = img + noise                                              # A
        ib = G.render(Ete[i], v, a, CLASSES[k][0], parts[s],
                      np.random.default_rng(int(i)), residuo=R.para_banda(r))   # B
        ic = G.escrever_simetria(img, R.para_permutacao(r))           # C

        if i == idx[0]:
            exemplos = {"A": ia, "B": ib, "C": ic}

        for tag, im in (("A", ia), ("B", ib), ("C", ic)):
            acc[tag]["classe_cru"].append(
                G.decode_body_alphabet(graphs(im[None], tau), Aa_r, lab_r)[0] == k)
            icn = G.ler_corpo_canonico(im)
            acc[tag]["classe_canon"].append(
                G.decode_body_alphabet(graphs(icn[None], tau), Aa_c, lab_c)[0] == k)
            c_, w_ = G.body_cont(icn, True)
            acc[tag]["classe_soft"].append(int(G.decode_body_cont(c_[None], w_[None], prot_c)[0]) == k)
            acc[tag]["carga"].append(G.decode_payload(im, bits, parts) == s)

        # o que cada roteamento devolve do PRÓPRIO resíduo
        for tag, got in (("A", None), ("B", R.recuperar_ordinal_banda(ib)),
                         ("C", R.ordem_de_permutacao(G.simetria_ordem(ic)))):
            ok = got is not None and np.array_equal(got, ord_true)
            acc[tag]["ordinal"].append(bool(ok))
            acc[tag]["corr"].append(0.0 if got is None
                                    else float(np.corrcoef(R.memoria(r), np.asarray(got, float))[0, 1]))

    out = {}
    for tag in ("A", "B", "C"):
        out[tag] = {m: float(np.mean(acc[tag][m])) for m in acc[tag]}
        out[tag]["linhas_ocupadas"] = linhas[tag]
    out["A"]["sigma_equivalente"] = float(np.mean(sigmas))
    out["energia_total_media"] = float(np.mean([np.sum(R.gerar(rng=np.random.default_rng(j)) ** 2)
                                                for j in range(20)]))

    # ---- figura ----
    fig, ax = plt.subplots(1, 5, figsize=(16, 4.2))
    rot = {"A": ("A: espalhado (σ≈0,11)", [9, 30], ["corpo", "carga"]),
           "B": ("B: banda 16-21", [9, 30, 57], ["corpo", "carga", "resíduo"]),
           "C": ("C: simetria (0 linhas)", [9, 30], ["corpo", "carga"])}
    for j, tag in enumerate(("A", "B", "C")):
        ax[j].imshow(exemplos[tag], cmap="gray", vmin=0, vmax=1, aspect="auto",
                     interpolation="nearest")
        ax[j].set_title(rot[tag][0], fontsize=9)
        ax[j].axhline(30 - 0.5, color="red", lw=0.6)
        if tag == "B": ax[j].axhline(48 - 0.5, color="deepskyblue", lw=0.6)
        ax[j].set_xticks([]); ax[j].set_yticks(rot[tag][1])
        ax[j].set_yticklabels(rot[tag][2], fontsize=7)
    tags = ("A", "B", "C"); w = 0.26
    for j, m in enumerate(("classe_cru", "classe_canon", "classe_soft")):
        ax[3].bar(np.arange(3) + (j - 1) * w, [out[t][m] for t in tags], w, label=m)
    ax[3].axhline(1 / 6, ls=":", c="k"); ax[3].set_xticks(range(3))
    ax[3].set_xticklabels(["A espalhado", "B banda", "C simetria"], fontsize=8)
    ax[3].set_title("classe (6 vias; acaso 0,167)"); ax[3].set_ylim(0, 1.02); ax[3].legend(fontsize=7)
    for j, m in enumerate(("carga", "ordinal", "corr")):
        ax[4].bar(np.arange(3) + (j - 1) * w, [out[t][m] for t in tags], w, label=m)
    ax[4].set_xticks(range(3)); ax[4].set_xticklabels(["A", "B", "C"], fontsize=8)
    ax[4].set_title("carga × recuperação do resíduo"); ax[4].set_ylim(0, 1.02); ax[4].legend(fontsize=7)
    fig.suptitle("E5 — a mesma energia de resíduo, três destinos", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "residuo.png"), dpi=130); plt.close(fig)
    return out


# ================= E6: agência (mão dupla) =================
def _perturb_fraco(img, canal, amp=0.03):
    """Estímulo fraco = mudança de FORMA num canal (mudança de nível puro é cancelada
    pela centralização do cosseno — só a forma do traçado vira aresta)."""
    b = img.reshape(-1, G.R, T_MUNDO).copy()
    b[4 + canal] += amp * np.sin(np.linspace(0, np.pi, T_MUNDO))
    return b.reshape(-1, T_MUNDO)


def e6_agencia(Ite, yte, tau0=0.7, passos=32, repouso=40, seed=1):
    """Mão dupla: o que é LIDO altera as PRÓPRRIAS regras de transição.

    1. trajetória fechada vs aberta sob o MESMO evento de resíduo;
    2. Filtro de Landauer ligado vs desligado (a energia descartada vira tensão);
    3. critério operacional: mesmo X, resíduo por canal diferente -> próxima transição
       (aberto = 0 exato; fechado > 0);
    4. temporariedade: sem leitura, S* e τ voltam ao normal;
    5. reatividade: τ normal vs τ exausto (densidade de arestas e probabilidade de
       reagir a um estímulo fraco) — o "mau humor" operacional.
    """
    eventos = [R.gerar(rng=np.random.default_rng(900 + t)) for t in range(passos)]
    ab = A.Agente(S_STAR, tau0=tau0, fechado=False, seed=seed)
    fc = A.Agente(S_STAR, tau0=tau0, fechado=True, landauer=True, seed=seed)
    fo = A.Agente(S_STAR, tau0=tau0, fechado=True, landauer=False, seed=seed)
    X0 = np.full(NV, 0.5)
    Xa, Xf, Xo = X0.copy(), X0.copy(), X0.copy()
    hist = {k: [] for k in ("t", "T_fech", "T_abert", "T_semL", "tau_fech",
                            "tau_abert", "S_fech", "S_abert")}
    for t in range(passos):
        Xa = ab.passo(Xa, eventos[t]); Xf = fc.passo(Xf, eventos[t]); Xo = fo.passo(Xo, eventos[t])
        hist["t"].append(t); hist["T_fech"].append(float(Xf[1])); hist["T_abert"].append(float(Xa[1]))
        hist["T_semL"].append(float(Xo[1])); hist["tau_fech"].append(fc.tau)
        hist["tau_abert"].append(ab.tau); hist["S_fech"].append(fc.s[1]); hist["S_abert"].append(ab.s[1])

    # 3. critério: mesmo X, resíduo POR CANAL (é o vetor que diferencia os pesos)
    s_dev_evento = float(fc.s[1] - S_STAR[1])
    tau_evento = float(fc.tau)
    res_vetor = np.array([0.50, 0.10, 0.42, 0.06, 0.30, 0.22])
    d_f, tau_f, tau_fn = A.criterio_mao_dupla(X0, fc, res_vetor)
    d_a, _, _ = A.criterio_mao_dupla(X0, ab, res_vetor)

    # 4. temporariedade: sem leitura, o alvo e o limiar voltam ao normal
    fc.landauer = False
    Xr = Xf.copy()
    for t in range(repouso):
        Xr = fc.passo(Xr, np.zeros((NV, T_MUNDO)))
        hist["t"].append(passos + t); hist["T_fech"].append(float(Xr[1]))
        hist["T_abert"].append(float(Xa[1])); hist["T_semL"].append(float(Xo[1]))
        hist["tau_fech"].append(fc.tau); hist["tau_abert"].append(ab.tau)
        hist["S_fech"].append(fc.s[1]); hist["S_abert"].append(ab.s[1])
    s_dev_repouso = float(fc.s[1] - S_STAR[1])

    # 5. reatividade: τ normal vs τ exausto, sobre glifos reais.
    #    O efeito não está na probabilidade TOTAL de reagir (fraca), está em PODER
    #    GANHAR relação nova: com τ alto o sistema só perde as que já tinha.
    rngp = np.random.default_rng(11)
    N = 1200
    ii = rngp.integers(0, len(Ite), N); cc = rngp.integers(0, NV, N)
    ids_dens = np.concatenate([np.where(yte == k)[0][:15] for k in range(6)])   # 90, um por classe
    reac = {}
    for t in (tau0, 0.90):
        reagiu, cria, apaga = [], [], []
        for j in range(N):
            alt = _perturb_fraco(Ite[ii[j]], int(cc[j]))
            ga, gb = G.body_graph(Ite[ii[j]], t), G.body_graph(alt, t)
            reagiu.append(bool((ga != gb).any()))
            cria.append(int(((gb - ga) > 0).sum())); apaga.append(int(((ga - gb) > 0).sum()))
        reac[f"{t}"] = dict(densidade_arestas=float(np.mean(graphs(Ite[ids_dens], t))),
                            prob_reagir=float(np.mean(reagiu)),
                            relacoes_ganhas=float(np.mean(cria)),
                            relacoes_perdidas=float(np.mean(apaga)))

    out = dict(
        distancia_trajetoria_fechado_vs_aberto=float(np.mean(np.abs(Xf - Xa))),
        tensao_final_landauer_on=float(Xf[1]), tensao_final_landauer_off=float(Xo[1]),
        tensao_final_aberto=float(Xa[1]),
        landauer_medio=float(np.mean(fc.log["landauer"])),
        criterio_mao_dupla_fechado=d_f, criterio_mao_dupla_aberto=d_a,
        tau_criterio_com_residuo=float(tau_f), tau_criterio_sem_residuo=float(tau_fn),
        tau_medio_fechado=float(np.mean(hist["tau_fech"][:passos])),
        tau_medio_aberto=float(np.mean(hist["tau_abert"][:passos])),
        tau0=tau0,
        s_star_desvio_max_evento=float(max(hist["S_fech"][:passos]) - S_STAR[1]),
        s_star_desvio_no_evento=s_dev_evento,
        s_star_desvio_apos_repouso=s_dev_repouso,
        tau_no_evento=tau_evento, tau_apos_repouso=float(fc.tau),
        reatividade=reac,
    )

    # ---- figura ----
    fig, ax = plt.subplots(2, 2, figsize=(11, 7))
    t_ = hist["t"]
    ax[0, 0].plot(t_, hist["T_fech"], label="fechado (Landauer on)", lw=1.6)
    ax[0, 0].plot(t_, hist["T_semL"], label="fechado (Landauer off)", lw=1.2, ls="--")
    ax[0, 0].plot(t_, hist["T_abert"], label="aberto (mão única)", lw=1.2)
    ax[0, 0].axvline(passos, color="gray", ls=":", lw=1); ax[0, 0].set_title("tensão X[T]")
    ax[0, 0].legend(fontsize=7)
    ax[0, 1].plot(t_, hist["tau_fech"], label="fechado"); ax[0, 1].plot(t_, hist["tau_abert"], label="aberto")
    ax[0, 1].axhline(tau0, ls=":", c="k", lw=1); ax[0, 1].axvline(passos, color="gray", ls=":", lw=1)
    ax[0, 1].set_title(f"limiar τ do RIC (τ0={tau0})"); ax[0, 1].legend(fontsize=7)
    ax[1, 0].plot(t_, hist["S_fech"], label="S* fechado"); ax[1, 0].plot(t_, hist["S_abert"], label="S* aberto")
    ax[1, 0].axhline(S_STAR[1], ls=":", c="k", lw=1); ax[1, 0].axvline(passos, color="gray", ls=":", lw=1)
    ax[1, 0].set_title("alvo de T (S*) — muda e volta"); ax[1, 0].legend(fontsize=7)
    ks = sorted(reac, key=float)
    labs = [f"τ={k}" for k in ks]; w = 0.26
    nome = {"densidade_arestas": "relações no glifo",
            "relacoes_ganhas": "ganhos sob estímulo fraco",
            "relacoes_perdidas": "perdas sob estímulo fraco"}
    for j, (m, cor) in enumerate([("densidade_arestas", "tab:orange"),
                                  ("relacoes_ganhas", "tab:blue"),
                                  ("relacoes_perdidas", "tab:red")]):
        ax[1, 1].bar(np.arange(len(ks)) + (j - 1) * w, [reac[k][m] for k in ks], w,
                     label=nome[m], color=cor)
    ax[1, 1].set_xticks(range(len(ks))); ax[1, 1].set_xticklabels(labs)
    ax[1, 1].set_title("reatividade: τ normal vs exausto"); ax[1, 1].legend(fontsize=7)
    for a in ax.ravel():
        a.grid(alpha=.3); a.set_xlabel("passo" if a is not ax[1, 1] else "τ")
    fig.suptitle("E6 — mão dupla: leitura → tensão/limiar → regras de transição", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "agencia.png"), dpi=130); plt.close(fig)
    return out


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

    # ---- E3: o 0,208 publicado é artefato de desempate; uma palavra por isomorfismo resolve ----
    pr_iso, bt_iso = G.codebook_up_to_isomorphism(D_CARGA)
    items_iso, r4 = [], np.random.default_rng(17)
    for _ in range(300):
        k = int(r4.integers(6)); e = make_set(1, int(r4.integers(1e6)))[0][k]
        v, a = affect(e); s = int(r4.integers(len(pr_iso)))
        items_iso.append((G.render(e, v, a, CLASSES[k][0], pr_iso[s], r4), s))
    limpo_iso, perm_iso = [], []
    for img, s in items_iso:
        limpo_iso.append(G.decode_payload(img, bt_iso, pr_iso) == s)
        perm_iso.append(G.decode_payload(G.t_perm(img, r4, ()), bt_iso, pr_iso, G.ALL_PERMS) == s)
    res["carga_isomorfismo"] = dict(
        codebook_padrao_palavras=len(pr), codebook_padrao_shapes=int(len({G.shape(p) for p in pr})),
        codebook_iso_palavras=len(pr_iso), codebook_iso_bits=float(np.log2(len(pr_iso))),
        iso_limpo=float(np.mean(limpo_iso)), iso_sob_permutacao=float(np.mean(perm_iso)),
        observacao="0,208 (número publicado) vem de palavras isomorfas empatando a distância "
                   "mínima no mesmo glifo; sem essa ambiguidade a carga sob permutação é ~1,0",
    )

    # ---- curva acurácia x sigma (leitor robusto) e os dois novos experimentos ----
    res["curva_sigma"] = curva_sigma(Itr, ytr, Ite, yte, tau)
    res["E5_residuo"] = e5_residuo(Itr, ytr, Ite, yte, ste, Ete, parts, bits, tau, n=300)
    res["E6_agencia"] = e6_agencia(Ite, yte, tau0=tau)

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
