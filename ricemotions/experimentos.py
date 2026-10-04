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
E7  MutaCore: o resíduo de transição (§B) reproduz o JSON publicado? E as previsões
    dele ("6c_nivel cai, 6c_relacional segura") valem no nosso pipeline?
E8  MutaCore: o benchmark de sobrevivência (§E) — reprodução fiel, ablação 2x2x2,
    varredura de severidade e o limiar exato em que a morte passa a ser possível.
E9  MutaCore: o espaço de chave da cifra acoplada ao resíduo (§F) e força bruta.

Análise, vereditos e provas: docs/06_analise_mutacore.md.
"""
import json, os, sys, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ricemotions.mundo import (CLASSES, CAUSAS, FAMILIAS, make_set, affect, VARS,
                               S_STAR, NV, T as T_MUNDO)
from ricemotions import glifo as G
from ricemotions import residuo as R
from ricemotions import agente as A
from ricemotions import homeostase as H

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


# ================= E7: o resíduo do MutaCore no nosso pipeline =================
def e7_residuo_mutacore(Ite, yte, ste, Ete, parts, avaliar):
    """E7 — o formalismo de resíduo do MutaCore (§B) medido no NOSSO pipeline.

    (1) reproduz o JSON publicado (γ=0,8, α_L=0,15, λ do 2º código do documento);
    (2) mede a MAGNITUDE do deslocamento Φ que esse formalismo injeta;
    (3) testa as previsões do documento — "6c_nivel sofre penalidade mensurável,
        6c_relacional mantém a estabilidade" — injetando Φ nos 300 episódios do
        teste e re-avaliando com o MESMO pipeline;
    (4) tem um CONTROLE: re-renderiza os episódios intactos com os mesmos RNGs,
        para separar efeito do resíduo de ruído de re-renderização;
    (5) repete com γ ampliado 10x (resíduo ~ sinal) e 100x (destruição), separando
        "efeito nulo" de "parâmetro publicado pequeno demais".
    """
    sim = H.simular_landauer()
    dif = max(abs(sim[k][c] - H.PUBLICADO[k][c]) for k in H.PUBLICADO for c in H.PUBLICADO[k])
    amp = float(np.ptp(H.roteiro_mutacore("alegria", "meta")[1]))      # sinal do roteiro

    def renderiza(epis):
        imgs = []
        for i, ep in enumerate(epis):
            v, a = affect(ep); k = int(yte[i])
            imgs.append(G.render(ep, v, a, CLASSES[k][0], parts[int(ste[i])],
                                 np.random.default_rng(7000 + i)))
        return np.array(imgs)

    CHAVES = ("6c_relacional", "6c_nivel", "3c_relacional", "pipeline_completo", "carga_acc")
    orig = avaliar(Ite, yte, ste)
    controle = avaliar(renderiza(list(Ete)), yte, ste)
    deltas = {"re-renderização (controle)": {k: float(controle[k] - orig[k]) for k in CHAVES}}
    for nome, mult in [("gamma_0.8", 1.0), ("gamma_x10", 10.0), ("gamma_x100", 100.0)]:
        eps2 = [H.injetar(ep, H.residuo_transicao(ep, gamma=H.GAMMA * mult)) for ep in Ete]
        d = avaliar(renderiza(eps2), yte, ste)
        deltas[nome] = {k: float(d[k] - controle[k]) for k in CHAVES}
    # o resíduo mudaria a FAMÍLIA afetiva de algum glifo?
    fam_ok = [((affect(H.injetar(ep))[0] > 0) == (FAM_OF[yte[i]] == 0)) for i, ep in enumerate(Ete)]
    return dict(
        reproducao_do_json_publicado=bool(dif < 5e-6), diferenca_max_json=dif,
        max_phi=float(sim["_max_phi"]), amplitude_do_sinal=amp,
        razao_phi_sinal=float(sim["_max_phi"] / amp),
        familia_afetiva_preservada=float(np.mean(fam_ok)),
        deltas=deltas,
        observacao="base = re-renderização controle com os MESMOS RNGs; "
                   "só o resíduo distingue as outras duas linhas",
    )


# ================= E8: benchmark de sobrevivência (MutaCore §E) =================
class _GlobalRNG:
    """Adaptador: o benchmark do documento usa np.random global nos dois robôs."""
    @staticmethod
    def random():
        return float(np.random.rand())


def e8_sobrevivencia(n=1000, sementes=50):
    """E8 — o benchmark de sobrevivência do MutaCore (§E), reproduzido e ablado.

    Três perguntas: (a) o documento mede de fato uma sobrevida maior? (b) a morte
    é sequer possível nos parâmetros publicados? (c) o que sobrevive — a política
    de recarga cedo ou a dinâmica de S*? Ver docs/06 §4.
    """
    AFI = dict(dinamico=True, generosa=True, esfria=0.10)   # "robô afetivo" do doc
    RIG = dict(dinamico=False, generosa=False, esfria=0.02)  # "robô linear" do doc
    dH_max = 0.15 * 0.8 ** 2 + 0.05 * 0.6                   # cpu=0.8, ruído=0,6

    def roda(**cfg):
        """Um robô isolado; devolve (ciclos, metas, E_min, T_max, defensivas)."""
        X, vivo, metas, defens = S_STAR.copy(), True, 0, 0
        minE, maxT = float(X[0]), float(X[1])
        rs = np.random.default_rng(cfg.pop("seed", 0))
        for t in range(n):
            X, vivo, dfv, meta = H.passo_robo(X, float(rs.uniform(0.1, 0.6)),
                                              t % 50 < 15, rng=rs, **cfg)
            metas += int(meta); defens += int(dfv)
            minE, maxT = min(minE, X[0]), max(maxT, X[1])
            if not vivo:
                break
        return dict(ciclos=t + 1, metas=metas,
                    E_min=minE, T_max=maxT, defensivas=defens)

    # (1) reprodução FIEL: os dois robôs no MESMO ruído, RNG global como no doc
    np.random.seed(42)
    Xa, Xl, va, vl = S_STAR.copy(), S_STAR.copy(), True, True
    traj = {"afetivo": [], "linear": []}
    met, cic = {"afetivo": 0, "linear": 0}, {"afetivo": 0, "linear": 0}
    minE, maxT = [1.0, 1.0], [0.0, 0.0]
    for t in range(n):
        env = float(np.random.uniform(0.1, 0.6)); cpu = (t % 50 < 15)
        if va:
            Xa, va, _, m = H.passo_robo(Xa, env, cpu, rng=_GlobalRNG(), **AFI)
            met["afetivo"] += int(m); cic["afetivo"] += 1
        if vl:
            Xl, vl, _, m = H.passo_robo(Xl, env, cpu, rng=_GlobalRNG(), **RIG)
            met["linear"] += int(m); cic["linear"] += 1
        minE[0], maxT[0] = min(minE[0], Xa[0]), max(maxT[0], Xa[1])
        minE[1], maxT[1] = min(minE[1], Xl[0]), max(maxT[1], Xl[1])
        if t % 10 == 0:
            traj["afetivo"].append([float(Xa[0]), float(Xa[1])])
            traj["linear"].append([float(Xl[0]), float(Xl[1])])
    fiel = dict(
        afetivo=dict(ciclos=cic["afetivo"], metas=met["afetivo"], E_min=minE[0], T_max=maxT[0]),
        linear=dict(ciclos=cic["linear"], metas=met["linear"], E_min=minE[1], T_max=maxT[1]))
    fiel["ganho_de_sobrevida_pct"] = 100.0 * (fiel["afetivo"]["ciclos"] - fiel["linear"]["ciclos"]) \
        / max(fiel["linear"]["ciclos"], 1)

    # (2) a morte é possível nos parâmetros publicados?
    limites = dict(ponto_fixo_max_de_T=float(dH_max / 0.15), limiar_de_T=0.95,
                   E_min_possivel_politica_rigida=float(0.20 - 0.015), limiar_de_E=0.0,
                   morte_possivel=bool(dH_max / 0.15 >= 0.95 or (0.20 - 0.015) <= 0))

    # (3) ablação 2x2x2 nos parâmetros do documento
    abl = {}
    for d in (False, True):
        for g in (False, True):
            for f in (False, True):
                nome = f"S*{'din' if d else 'fix'}|pol{'tensao' if g else 'E<0.20'}|esfria{f}"
                abl[nome] = roda(dinamico=d, generosa=g, esfria=0.10 if f else 0.02, seed=0)

    # (4) varredura de severidade: o gasto por ciclo é o que decide
    CFG3 = [("afetiva (S*din+tensão)", AFI),
            ("S*fixo+tensão (abla S*)", dict(dinamico=False, generosa=True, esfria=0.10)),
            ("rígida (E<0.20)", RIG)]
    varredura = {}
    for gasto in (0.015, 0.10, 0.12, 0.125, 0.15):
        varredura[f"{gasto}"] = {nome: roda(seed=0, gasto=gasto, **dict(cfg))["ciclos"]
                                 for nome, cfg in CFG3}

    # (5) regime letal: 50 sementes, o que a dinâmica de S* faz com a sobrevivência
    letal = {}
    for nome, cfg in [("afetivo (S*din + tensao)", dict(dinamico=True, generosa=True, esfria=0.10)),
                      ("S*FIXO + tensao (abla S*)", dict(dinamico=False, generosa=True, esfria=0.10)),
                      ("linear rigido (E<0.20)", dict(dinamico=False, generosa=False, esfria=0.02))]:
        v = [roda(seed=s, gasto=0.13, **dict(cfg))["ciclos"] for s in range(sementes)]
        letal[nome] = dict(media=float(np.mean(v)), desvio=float(np.std(v)),
                           min=int(np.min(v)), max=int(np.max(v)))
    efeito = letal["afetivo (S*din + tensao)"]["media"] - letal["S*FIXO + tensao (abla S*)"]["media"]
    return dict(reproducao_fiel=fiel, limites_analiticos=limites, ablacao=abl,
                varredura_de_severidade=varredura, regimeletal=letal,
                efeito_do_S_dinamico_ciclos=float(efeito),
                observacao="nos parâmetros publicados ambos sobrevivem 1000/1000 e a "
                           "linha 'SUCESSO DA CAMADA 3' nunca imprime",
                trajeto=traj)


# ================= E9: chave acoplada ao resíduo (MutaCore §F) =================
def e9_chave_residuo():
    """E9 — a cifra cuja chave é o resíduo: quantos bits ela realmente tem?"""
    parts, _ = G.codebook(D_CARGA)
    base = len(parts)
    msg, achados = "MutaCore v2", 0
    dig = G.text_to_digits(msg, base)

    def cifra(d, residuo, rev=False):
        seed = int(np.round(residuo * 100000)) & 0xFFFFFFFF
        ks = np.random.default_rng(seed).integers(0, base, size=len(d))
        return [(int(x) - int(k)) % base if rev else (int(x) + int(k)) % base
                for x, k in zip(d, ks)]

    cip = cifra(dig, 0.034521)
    t0 = time.time()
    chave = None
    for s in range(100001):                       # espaço real: round(resíduo*1e5)
        achados += 1
        if G.digits_to_text(cifra(cip, s / 100000.0, True), base) == msg:
            chave = s / 100000.0
            break
    return dict(mensagem=msg, simbolos=len(dig), base=base,
                espaco_de_chave=100001, bits_de_chave=float(np.log2(100001)),
                candidatos_testados=achados, chave_recuperada=chave,
                segundos=round(time.time() - t0, 3),
                roundtrip_com_chave_exata=(G.digits_to_text(cifra(cip, 0.034521, True), base) == msg),
                observacao="o documento chama isso de One-Time Pad; com "
                           "<17 bits de chave a força bruta é trivial (docs/06 §6)")


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
    # ---- MutaCore (docs/06): o que passou na análise, medido aqui ----
    res["E7_residuo_mutacore"] = e7_residuo_mutacore(Ite, yte, ste, Ete, parts, evaluate)
    res["E8_sobrevivencia"] = e8_sobrevivencia()
    res["E9_chave_residuo"] = e9_chave_residuo()

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
    # 5) MutaCore: o que foi reproduzido e o que foi refutado (docs/06)
    fig, ax = plt.subplots(2, 2, figsize=(11, 7.5))
    for fam in FAMILIAS:
        for cause in CAUSAS:
            Rl = H.residuo_transicao(H.roteiro_mutacore(fam, cause))
            if Rl.max() > 0:
                ax[0, 0].plot(Rl, label=f"{fam}-{cause}")
    e7 = res["E7_residuo_mutacore"]
    ax[0, 0].set_title(f"MutaCore R_L (reproduz o JSON: {e7['reproducao_do_json_publicado']})")
    ax[0, 0].set_xlabel("passo t"); ax[0, 0].set_ylabel("R_L")
    ax[0, 0].legend(fontsize=7); ax[0, 0].grid(alpha=.3)
    ax[0, 0].text(0.98, 0.62, f"|Φ|máx = {e7['max_phi']:.3f}\n= {e7['razao_phi_sinal']:.1%} do sinal",
                  transform=ax[0, 0].transAxes, ha="right", fontsize=8)

    tr = res["E8_sobrevivencia"]["trajeto"]; xs = np.arange(len(tr["afetivo"])) * 10
    ax[0, 1].plot(xs, [p[0] for p in tr["afetivo"]], label="E afetivo")
    ax[0, 1].plot(xs, [p[1] for p in tr["afetivo"]], label="T afetivo")
    ax[0, 1].plot(xs, [p[0] for p in tr["linear"]], "--", label="E linear")
    ax[0, 1].plot(xs, [p[1] for p in tr["linear"]], "--", label="T linear")
    ax[0, 1].axhline(0.95, color="red", ls=":", lw=1)
    ax[0, 1].text(320, 0.958, "morte por T", color="red", fontsize=7)
    ax[0, 1].set_ylim(0, 1.0); ax[0, 1].set_xlabel("ciclo")
    ax[0, 1].set_title(f"Benchmark: {res['E8_sobrevivencia']['reproducao_fiel']['afetivo']['ciclos']}/1000 e "
                       f"{res['E8_sobrevivencia']['reproducao_fiel']['linear']['ciclos']}/1000 vivos")
    ax[0, 1].legend(fontsize=7, ncol=2); ax[0, 1].grid(alpha=.3)

    var = res["E8_sobrevivencia"]["varredura_de_severidade"]
    gast = sorted(float(k) for k in var)
    for nome in var[f"{gast[0]}"]:
        ax[1, 0].plot(gast, [var[f"{g}"][nome] for g in gast], "o-", label=nome)
    ax[1, 0].axhline(1000, color="gray", ls="--", lw=0.8)
    ax[1, 0].axvline(0.015, color="black", ls=":", lw=1)
    ax[1, 0].set_xlabel("gasto de energia por ciclo"); ax[1, 0].set_ylabel("ciclos sobrevividos")
    ax[1, 0].set_title("A morte é do GASTO (publicado 0,015), não da emoção")
    ax[1, 0].legend(fontsize=7); ax[1, 0].grid(alpha=.3)

    d7 = res["E7_residuo_mutacore"]["deltas"]
    labs = [l for l in d7 if "x100" not in l]      # γ×100 destrói o glifo: fora de escala
    w7 = 0.36
    for j, k in enumerate(["6c_relacional", "6c_nivel"]):
        vals = [d7[l][k] for l in labs]
        barras = ax[1, 1].bar(np.arange(len(labs)) + (j - 0.5) * w7, vals, w7, label=k)
        for rect, v in zip(barras, vals):
            ax[1, 1].text(rect.get_x() + rect.get_width() / 2, v - 0.004 if v < 0 else 0.002,
                          f"{v:+.3f}", ha="center", va="top" if v < 0 else "bottom", fontsize=6)
    ax[1, 1].axhline(0, c="k", lw=1)
    ax[1, 1].set_ylim(-0.085, 0.032)
    ax[1, 1].set_xticks(range(len(labs))); ax[1, 1].set_xticklabels(labs, rotation=12, fontsize=7)
    ax[1, 1].set_ylabel("Δ acurácia vs controle")
    ax[1, 1].set_title("Previsão: 'nível cai, relacional segura'")
    ax[1, 1].text(0.99, 0.97, f"γ×100 (destruição): {d7['gamma_x100']['6c_relacional']:+.2f} relacional / "
                              f"{d7['gamma_x100']['6c_nivel']:+.2f} nível",
                  transform=ax[1, 1].transAxes, ha="right", va="top", fontsize=7)
    ax[1, 1].legend(fontsize=7, loc="lower left"); ax[1, 1].grid(alpha=.3, axis="y")
    fig.suptitle("MutaCore/RIC: reprodução, magnitude e ablação (docs/06)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "mutacore.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
