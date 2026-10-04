"""
Experimentos do trabalho EMOÇÃO COM PROCEDÊNCIA (TEOA x RIC)

E1  Três alegrias (e três tristezas): a procedência se lê nas RELAÇÕES do corpo do glifo?
    relacional (RIC) vs nível vs delta vs nível+delta; limpo e sob transformações da imagem.
E2  Família afetiva: canal de NÍVEL (faixa de intensidade) vs canal RELACIONAL (par de linhas).
E3  Carga explícita: capacidade x robustez (d_min), permutação de vértices, mensagem em vários glifos.
E4  Pipeline completo (família por polaridade + procedência por relações) vs linhas de base.
E5  Resíduo do ambiente: o mesmo estado residual em três codificações
    (espalhado | banda | simetria).
E6  Agência: Landauer -> T/C -> tau -> pesos -> transição (mão dupla vs roteiro).
    + curva acurácia x sigma do leitor robusto (correção de atenuação por redundância).
E7  MutaCore: o resíduo de transição (§B) reproduz o JSON publicado? E as previsões
    dele ("6c_nivel cai, 6c_relacional segura") valem no nosso pipeline?
E8  MutaCore: o benchmark de sobrevivência (§E) — reprodução fiel, ablação 2x2x2,
    varredura de severidade e o limiar exato em que a morte passa a ser possível.
E9  MutaCore: o espaço de chave da cifra acoplada ao resíduo (§F) e força bruta.
E10 Orçamento igual: o resíduo supera uma memória convencional de MESMO orçamento?
    Quatro agentes (A0/AN/AM/AR), três condições (pouco conteúdo passado, informação
    preditiva do futuro, J) — especificação do documento MUTARIC ev (docs/09).
E10b Controles fortes de memória com 24 bits por agente (EMA assinada, magnitude,
    janela curta, recorrente aprendido; ID + OOD) — port fiel do e10b.py externo
    (auditoria MUTARIC ev 2, docs/10): a formulação forte é refutada e isto é
    publicado com a mesma proeminência dos resultados positivos.

Análise, vereditos e provas: docs/06_analise_mutacore.md, docs/09_analise_mutaric_ev.md
e docs/10_analise_mutaric_ev2.md (E10b: controles fortes de memória, 24 bits).
Coleta REAL de informação desta máquina (não determinística, fora do run_all):
    python -m ricemotions.experimentos --telemetria
"""
import json, os, sys, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ricemotions.mundo import (CLASSES, CAUSAS, FAMILIAS, make_set, affect, VARS,
                               S_STAR, NV, T as T_MUNDO, episode)
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
    """O MESMO estado residual (energia média Σr² = 17,3) em três codificações.

    As três rotas partem da MESMA realização de resíduo; o que cada uma faz com ela
    é que difere (a energia medida na SAÍDA de cada rota não é a mesma grandeza).

    ``A espalhado`` vira ruído de pixel (é o modelo das E1-E4) — destrói a leitura.
    ``B banda``     linhas-de-patch 16-21 dedicadas — leitura intacta, custa 6 linhas.
    ``C simetria``  vira uma permutação do corpo canônico — leitura intacta, custa
                    ZERO linhas e carrega a ORDEM dos 6 canais: teto combinatório
                    log2 720 = 9,49 bits (não é capacidade útil — são os 6 lugares
                    da ordenação; empates e a distribuição limitam o que se recupera).

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
    fig.suptitle("E5 — o mesmo estado residual, três codificações", fontsize=11)
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
                            "tau_abert", "tau_semL", "S_fech", "S_abert")}
    for t in range(passos):
        Xa = ab.passo(Xa, eventos[t]); Xf = fc.passo(Xf, eventos[t]); Xo = fo.passo(Xo, eventos[t])
        hist["t"].append(t); hist["T_fech"].append(float(Xf[1])); hist["T_abert"].append(float(Xa[1]))
        hist["T_semL"].append(float(Xo[1])); hist["tau_fech"].append(fc.tau)
        hist["tau_abert"].append(ab.tau); hist["tau_semL"].append(fo.tau)
        hist["S_fech"].append(fc.s[1]); hist["S_abert"].append(ab.s[1])

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
        hist["tau_semL"].append(fo.tau)
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
        tau_medio_landauer_off=float(np.mean(hist["tau_semL"][:passos])),
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
                campos_nao_deterministicos=["segundos"],
                observacao="o documento chama isso de One-Time Pad; com "
                           "<17 bits de chave a força bruta é trivial (docs/06 §6). "
                           "'segundos' varia por máquina e está declarado aqui como "
                           "NÃO determinístico: nenhum teste regressa esse campo "
                           "(MUTARIC ev, correção 1 — docs/09 §3)")


# ================= E10: orçamento igual (MUTARIC ev §6 — docs/09) =================
E10_PARAM = dict(T_passos=160, sementes=25, bloco=8, k_pred=5, alpha=0.15, k_w=0.8,
                 dt=0.30, ruido=0.004, beta_mundo=0.35, l1=1.0, l2=0.0, l3=0.0,
                 l4=0.5, eps=0.10, bins=5, seed_base=3000)
E10_AGENTES = ("A0", "AN", "AM", "AR")


def _e10_fluxo(sementes, T_passos, bloco, seed_base, fator=None):
    """Fluxo do mundo: um episódio por passo, classe em BLOCOS de `bloco` passos.

    A estrutura em blocos é ESCOLHA DE PROJETO (documentada em docs/09 §5): sem
    estrutura temporal no mundo, "prever o futuro" não significa nada.

    Devolve (medias, desv, turb), shape (sementes, T_passos, 6):
      medias — conteúdo: média por canal do episódio (o que um leitor apagaria);
      desv   — desvio padrão por canal do episódio (features para a condição (a));
      turb   — turbulência: |medias_t − medias_{t−1}| (magnitudes de mudança).
    `fator` (T_passos,) escala a turbulência — é por aqui que a TELEMETRIA REAL da
    máquina entra no lugar do resíduo sintético (variante real, não determinística).
    """
    medias = np.zeros((sementes, T_passos, NV))
    desv = np.zeros((sementes, T_passos, NV))
    turb = np.zeros((sementes, T_passos, NV))
    for s in range(sementes):
        rng = np.random.default_rng(seed_base + 1000 + s)
        prev = None
        for t in range(T_passos):
            k = (t // bloco + 3 * s) % len(CLASSES)
            e = episode(CLASSES[k][0], CLASSES[k][1], rng)
            medias[s, t] = e.mean(1)
            desv[s, t] = e.std(1)
            if prev is not None:
                turb[s, t] = np.abs(medias[s, t] - prev)
            prev = medias[s, t]
    if fator is not None:
        turb = turb * np.asarray(fator, float)[None, :, None]
    return medias, desv, turb


def _e10_ema(x, alpha):
    """Mesma regra de `residuo.memoria_ema`: (1−α)·antigo + α·novo, começando em 0."""
    out = np.zeros_like(x)
    out[:, 0] = alpha * x[:, 0]
    for t in range(1, x.shape[1]):
        out[:, t] = (1 - alpha) * out[:, t - 1] + alpha * x[:, t]
    return out


def _e10_sinais(medias, turb, alpha, seed_an):
    """Os quatro sinais — MESMO orçamento: 6 float64, mesma EMA α, mesma política.

    A0  sem memória (sinal nulo ⇒ w = 1, igual à baseline do A0 do documento).
    AN  ruído i.i.d. com (μ, σ) por canal do AR — controle de amplitude.
    AM  memória convencional reconstrutiva: EMA do CONTEÚDO (médias por canal).
    AR  resíduo MUTARIC: EMA das MAGNITUDES de mudança (regra de `memoria_ema`).
    """
    am = _e10_ema(medias, alpha)
    ar = _e10_ema(turb, alpha)
    mu, sd = ar.mean((0, 1)), ar.std((0, 1)) + 1e-9
    an = np.random.default_rng(seed_an).normal(mu, sd, size=ar.shape)
    return {"A0": np.zeros_like(ar), "AN": an, "AM": am, "AR": ar}


def _e10_roda(medias, turb, sinais, p):
    """Loop dos 4 agentes: mesma transição (`agente.transicao`), MESMO ruído por
    semente, mesmo alvo fixo S_STAR — só o sinal que modula `w` difere.

    Dois regimes de distúrbio (a fonte do distúrbio pode favorecer um memória ou
    outra; por isso os DOIS são reportados, sem escolher o regime depois de ver):
      conteudo  dist = β·(conteúdo − 0,5)         favorece quem lembra do conteúdo
      mudanca   dist = β·(conteúdo_t − conteúdo_{t−1})  favorece quem detecta mudança
    """
    S, Tp, _ = medias.shape
    beta = p["beta_mundo"]
    dists = {"conteudo": beta * (medias - 0.5),
             "mudanca": np.concatenate([np.zeros((S, 1, NV)), np.diff(medias, axis=1)], axis=1)}
    dists["mudanca"] = beta * dists["mudanca"]
    out, curvas = {}, {}
    for reg, dist in dists.items():
        J = {a: [] for a in sinais}; dm = {a: [] for a in sinais}; curva = {}
        for s in range(S):
            for a, sig in sinais.items():
                rng = np.random.default_rng(p["seed_base"] + 777 + s)  # MESMO ruído p/ todos
                X = np.full(NV, 0.5); ds = []
                for t in range(Tp):
                    el = sig[s, t]
                    w = np.clip(1.0 + p["k_w"] * (el - el.mean()), 0.3, 2.0)
                    X = A.transicao(X, S_STAR, w, rng, dt=p["dt"], ruido=p["ruido"])
                    X = np.clip(X + dist[s, t], 0.0, 1.0)               # distúrbio do mundo
                    ds.append(float(np.mean(np.abs(X - S_STAR))))
                ds = np.asarray(ds)
                # J = −λ1·distância média + λ4·fração perto do alvo (λ2=λ3=0:
                # nenhuma variante tem ação e o custo de cómputo é idêntico por construção)
                J[a].append(-p["l1"] * float(ds.mean()) + p["l4"] * float(np.mean(ds < p["eps"])))
                dm[a].append(float(ds.mean()))
                if s == 0:
                    curva[a] = [round(float(v), 4) for v in ds[::4]]
        out[reg] = dict(J={a: float(np.mean(v)) for a, v in J.items()},
                        J_dp={a: float(np.std(v)) for a, v in J.items()},
                        # MESMAS sementes em todos os agentes ⇒ comparação PAREADA
                        # (a diferença por semente cancela a variação do mundo)
                        delta_pareado={f"{x}-{z}":
                                       dict(media=float((np.asarray(J[x]) - np.asarray(J[z])).mean()),
                                            dp=float((np.asarray(J[x]) - np.asarray(J[z])).std()))
                                       for x, z in (("AR", "AM"), ("AR", "A0"),
                                                    ("AM", "A0"), ("AN", "A0"))},
                        distancia_media={a: float(np.mean(v)) for a, v in dm.items()})
        curvas[reg] = curva
    return out, curvas


def _e10_mi(x, y, bins=5):
    """MI empírica por histograma (bins × bins), em bits. x, y já emparelhados."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return 0.0                                # sinal constante ⇒ MI = 0
    h, _, _ = np.histogram2d(x, y, bins=bins)
    p = h / h.sum()
    px, py = p.sum(1), p.sum(0)
    nz = p > 0
    return float(np.sum(p[nz] * np.log2(p[nz] / (px[:, None] * py[None, :])[nz])))


def _e10_rmse(sig, feat, corte=0.7):
    """RMSE de teste ao reconstruir `feat` (12,) de `sig` (6,) — regressão linear
    com intercepto (lstsq) e SPLIT TEMPORAL 70/30 (sem vazamento temporal)."""
    n = len(sig); c = int(corte * n)
    Xtr = np.hstack([sig[:c], np.ones((c, 1))])
    Xte = np.hstack([sig[c:], np.ones((n - c, 1))])
    coef, *_ = np.linalg.lstsq(Xtr, feat[:c], rcond=None)
    return float(np.sqrt(np.mean((Xte @ coef - feat[c:]) ** 2)))


def _e10_condicoes(medias, desv, sinais, turb, p):
    """As três condições do documento (MUTARIC ev §6):
    (a) pouco conteúdo do passado no resíduo; (b) informação preditiva do futuro;
    (c) J(AR) > J(AM). MI por histograma, sempre comparada ao PISO do viés
    (MI de pares embaralhados) — MI empírica nunca é < 0, então o que se afirma
    é o MI EXCEDENTE ao embaralhado."""
    Tp = medias.shape[1]; k = p["k_pred"]; bins = p["bins"]
    # ordenação temporal (t, s) para o split 70/30 ser temporal de verdade
    tim = lambda x: x.transpose(1, 0, 2).reshape(-1, x.shape[-1])
    feat = tim(np.concatenate([medias, desv], -1))                 # (T·S, 12)
    rmse = {a: _e10_rmse(tim(sg), feat) for a, sg in sinais.items()}
    y = np.linalg.norm(turb[:, k:, :], axis=2).ravel()             # carga futura em t+k
    rng_sh = np.random.default_rng(p["seed_base"] + 91)
    yp = rng_sh.permutation(y)
    mi, mib = {}, {}
    for a, sg in sinais.items():
        per, perb = [], []
        for i in range(NV):
            x = sg[:, :Tp - k, i].ravel()
            per.append(_e10_mi(x, y, bins))
            perb.append(_e10_mi(x, yp, bins))
        mi[a] = float(np.mean(per)); mib[a] = float(np.mean(perb))
    exe = {a: mi[a] - mib[a] for a in sinais}
    return rmse, mi, mib, exe


def _e10_completo(fator=None, origem="sintético: resíduo derivado dos próprios episódios (seed fixa)"):
    """E10 completo: sinal → quatro agentes → J nos 2 regimes + condições (a)/(b)."""
    p = dict(E10_PARAM)
    medias, desv, turb = _e10_fluxo(p["sementes"], p["T_passos"], p["bloco"],
                                    p["seed_base"], fator=fator)
    sinais = _e10_sinais(medias, turb, p["alpha"], seed_an=p["seed_base"] + 55)
    rod, curvas = _e10_roda(medias, turb, sinais, p)
    rmse, mi, mib, exe = _e10_condicoes(medias, desv, sinais, turb, p)
    cond = dict(
        a_ar_reconstroi_menos_que_am=bool(rmse["AR"] > rmse["AM"]),
        b_mi_excesso_ar_positivo=bool(exe["AR"] > 0),
        c_j_ar_maior_que_am_conteudo=bool(rod["conteudo"]["J"]["AR"] > rod["conteudo"]["J"]["AM"]),
        c_j_ar_maior_que_am_mudanca=bool(rod["mudanca"]["J"]["AR"] > rod["mudanca"]["J"]["AM"]),
    )
    cond["c_ar_maior_nos_dois_regimes"] = bool(cond["c_j_ar_maior_que_am_conteudo"] and
                                               cond["c_j_ar_maior_que_am_mudanca"])
    n = int(cond["a_ar_reconstroi_menos_que_am"]) + int(cond["b_mi_excesso_ar_positivo"]) + \
        int(cond["c_ar_maior_nos_dois_regimes"])
    par = {r: rod[r]["delta_pareado"] for r in rod}
    d_am = par["conteudo"]["AR-AM"]["media"]
    d_a0 = par["conteudo"]["AR-A0"]["media"]
    return dict(
        origem_eventos=origem,
        deterministico=bool(fator is None),
        design=dict(p, agentes=list(E10_AGENTES),
                    politica="w = clip(1 + k_w·(s − média(s)), 0,3, 2); transicao() de agente.py; "
                             "alvo fixo S_STAR; MESMO ruído por semente em todos os agentes",
                    orcamento="6 float64 + mesma EMA α por agente; mesmos episódios, "
                              "sementes, horizonte e custo (λ2=λ3=0 por construção)",
                    condicoes="(a) RMSE de reconstrução dos 12 features do conteúdo, split temporal "
                              "70/30 · (b) MI(s_t; ||turb_{t+k}||) menos o piso embaralhado, "
                              "k=5, histograma 5 bins · (c) J(AR) > J(AM) nos DOIS regimes",
                    curvas="semente 0, 1 a cada 4 passos"),
        J={r: rod[r]["J"] for r in rod},
        J_dp={r: rod[r]["J_dp"] for r in rod},
        distancia_media={r: rod[r]["distancia_media"] for r in rod},
        cond_a_rmse_reconstrucao=rmse,
        cond_b_mi_bits=mi, cond_b_mi_embaralhado_bits=mib, cond_b_mi_excesso=exe,
        condicoes=cond,
        comparacoes_pareadas=par,
        veredito=f"{n} de 3 condições principais satisfeitas "
                 f"((a) AR reconstrói menos conteúdo que AM = {cond['a_ar_reconstroi_menos_que_am']}; "
                 f"(b) MI excedente de AR > 0 = {cond['b_mi_excesso_ar_positivo']}; "
                 f"(c) J(AR) > J(AM) nos dois regimes = {cond['c_ar_maior_nos_dois_regimes']}). "
                 f"Mas o ganho de AR sobre a NÃO-memória (A0) é {d_a0:+.4f} e sobre a memória "
                 f"convencional é {d_am:+.4f} no regime conteudo — ver comparacoes_pareadas: "
                 f"o resíduo supera a memória convencional, não a ausência de memória.",
        curvas=curvas,
    )


def e10_orcamento():
    """E10 — orçamento igual: o resíduo supera uma memória convencional do MESMO
    tamanho? Determinístico (só episódios com seed fixa) — é o que entra no JSON."""
    return _e10_completo()


def e10_telemetria_real(carga):
    """E10 com a turbulência escalada pela carga REAL desta máquina (psutil).

    É o "substituir os dados sintéticos": o fator de entrada deixa de ser 1.0 fixo
    e passa a vir da série de carga capturada (interpolação linear ao longo dos
    passos). NÃO determinístico — gravado em resultados/telemetria_real.json,
    nunca regressado por teste.
    """
    p = dict(E10_PARAM)
    c = np.asarray(carga, float)
    carga_i = np.interp(np.linspace(0, 1, p["T_passos"]), np.linspace(0, 1, len(c)), c)
    out = _e10_completo(fator=0.4 + 1.2 * carga_i,
                        origem="TELEMETRIA REAL desta máquina (psutil): turbulência × "
                               "(0,4 + 1,2·carga), carga interpolada ao longo dos passos")
    out["carga_interpolada"] = [round(float(v), 4) for v in carga_i]
    return out


def coleta_telemetria(amostras=10, intervalo=1.0):
    """Coleta INFORMAÇÃO REAL desta máquina + amostragem ao vivo de carga, e roda o
    E10 com a carga real no lugar do resíduo sintético.

    Grava DOIS arquivos fora do resultados.json (nenhum teste os regressa):
      resultados/maquina.json         descrição estática da máquina (metadados)
      resultados/telemetria_real.json amostras ao vivo + E10-real (NÃO determinístico)

    Nunca roda dentro de run_all.py nem da CI (reprodutibilidade). Requer psutil.
    """
    import platform
    import datetime
    try:
        import psutil
    except ImportError:
        return {"erro": "psutil não instalado — `pip install psutil` para coletar"}
    os.makedirs(RES, exist_ok=True)
    estatico = dict(
        sistema=f"{platform.system()} {platform.release()}",
        edicao=platform.version(),
        arquitetura=platform.machine(),
        processador=platform.processor() or "desconhecido",
        nucleos_logicos=os.cpu_count(),
        memoria_total_gb=round(psutil.virtual_memory().total / 2 ** 30, 2),
        disco_total_gb=round(psutil.disk_usage(RAIZ).total / 2 ** 30, 2),
        python=sys.version.split()[0],
        numpy=np.__version__, matplotlib=matplotlib.__version__, psutil=psutil.__version__,
        papel="metadados da máquina que produz os números publicados; não participa "
              "de nenhum teste nem de run_all.py",
    )
    cpu, mem, carga = [], [], []
    for _ in range(int(amostras)):
        cpu.append(float(psutil.cpu_percent(interval=float(intervalo))))
        mem.append(float(psutil.virtual_memory().percent))
        carga.append(0.5 * cpu[-1] / 100.0 + 0.5 * mem[-1] / 100.0)
    try:
        st = psutil.sensors_temperatures() or {}
        temps = {k: float(np.mean([x.current for x in v])) for k, v in st.items() if v}
    except (AttributeError, NotImplementedError):
        temps = {}
    with open(os.path.join(RES, "maquina.json"), "w", encoding="utf-8") as f:
        json.dump(estatico, f, indent=1, ensure_ascii=False)
    real = e10_telemetria_real(carga)
    real.update(quando_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                cpu_pct=cpu, ram_pct=mem, temperaturas_C=temps,
                amostras=int(amostras), intervalo_s=float(intervalo),
                deterministico=False,
                aviso="hardware real: estes valores mudam a cada coleta; nenhum teste "
                      "regride este arquivo (regra da correção 1 — docs/09 §3)")
    with open(os.path.join(RES, "telemetria_real.json"), "w", encoding="utf-8") as f:
        json.dump(real, f, indent=1, ensure_ascii=False)
    return dict(maquina=estatico, telemetria_real=real["veredito"], arquivos=[
        "resultados/maquina.json", "resultados/telemetria_real.json"])


# =========================================================================
# E10b — controles fortes de memória, orçamento de 24 bits
# Port FIEL do e10b.py externo (auditoria MUTARIC ev 2 — docs/10): a execução
# local do arquivo deles (2026-10-04, 108 s) reproduziu 58/58 números; este
# port regera exatamente os mesmos valores (test_e10b_reproduz_o_documento).
# Resultado: o resíduo quadrático NÃO vence as memórias fortes de igual
# orçamento — refutação da formulação forte, publicada com a mesma
# proeminência (regra do projeto). Determinístico: tudo é semeado.
# =========================================================================
E10B_N = 6                       # canais
E10B_BITS = 4                    # bits por canal (quantizador Q4)
E10B_BUDGET = E10B_N * E10B_BITS  # 24 bits mutáveis por agente
E10B_KINDS = ("none", "signed_ema", "magnitude_ema",
              "square_ema", "short_window", "learned_recurrent")
E10B_CFG = dict(steps=360, block=45, alpha=0.18, base_gain=0.10,
                memory_gain=0.38, action_budget=1.0, low=0.010,
                high=0.090, ood_scale=1.35, target=0.72,
                train_sequences=180, ridge=1e-3)


def _e10b_q(x, bits=E10B_BITS):
    """Quantizador de `bits` grades: clip em [0,1] e rótulo na grade de 1/15."""
    lev = 2 ** bits - 1
    return np.rint(np.clip(x, 0, 1) * lev) / lev


def _e10b_schedule(c, rng, ood):
    """Blocos com um canal 'quente' por bloco; OOD encurta o bloco (mais trocas)."""
    block = max(12, c["block"] // 2) if ood else c["block"]
    nb = int(np.ceil(c["steps"] / block)); order = []
    while len(order) < nb:
        order.extend(rng.permutation(E10B_N).tolist())
    return np.repeat(order[:nb], block)[:c["steps"]]


def _e10b_dseq(seed, c, ood=False):
    """Perturbações de média nula; o canal quente tem variância `high` (OOD: ×1,35)."""
    rng = np.random.default_rng(seed)
    hot = _e10b_schedule(c, rng, ood); arr = []
    for h in hot:
        sig = np.full(E10B_N, c["low"])
        sig[h] = c["high"] * (c["ood_scale"] if ood else 1.0)
        arr.append(rng.normal(0, sig))
    return np.asarray(arr)


def _e10b_train(c):
    """Ridge: y_(t+1) ~= [y_t, u_t, 1]·W com u = Δ² normalizado (só sementes de treino)."""
    X, Y = [], []
    for s in range(c["train_sequences"]):
        d = _e10b_dseq(100000 + s, c, False)
        u = np.clip(d * d / c["high"] ** 2, 0, 1); prev = np.zeros(E10B_N)
        for t in range(len(u) - 1):
            X.append(np.r_[prev, u[t], 1.0]); Y.append(u[t + 1]); prev = u[t + 1]
    X = np.asarray(X); Y = np.asarray(Y)
    reg = c["ridge"] * np.eye(X.shape[1]); reg[-1, -1] = 0
    return np.linalg.solve(X.T @ X + reg, X.T @ Y)


class _e10b_Store:
    """Estado mutável de UM agente. `square_ema` É o resíduo quadrático."""

    def __init__(self, kind, c, W=None):
        self.kind = kind; self.c = c
        self.z = np.zeros(E10B_N); self.W = W
        self.packed = 0; self.phase = 0

    def salience(self):
        if self.kind == "none":
            return np.zeros(E10B_N)
        if self.kind == "signed_ema":
            return np.abs(2 * self.z - 1)
        if self.kind == "short_window":
            vals = np.array([(self.packed >> (2 * i)) & 3
                             for i in range(2 * E10B_N)]).reshape(2, E10B_N)
            return vals.mean(0) / 3.0
        return self.z

    def update(self, d):
        c = self.c; a = c["alpha"]; sc = c["high"]
        if self.kind == "none":
            pass
        elif self.kind == "signed_ema":
            u = .5 + .5 * np.clip(d / sc, -1, 1)
            self.z = _e10b_q((1 - a) * self.z + a * u)
        elif self.kind == "magnitude_ema":
            u = np.clip(np.abs(d) / sc, 0, 1)
            self.z = _e10b_q((1 - a) * self.z + a * u)
        elif self.kind == "square_ema":
            u = np.clip(d * d / (sc * sc), 0, 1)
            self.z = _e10b_q((1 - a) * self.z + a * u)
        elif self.kind == "short_window":
            # 2 amostras × 2 bits × 6 canais = exatamente 24 bits em UM inteiro
            vals = np.rint(np.clip(np.abs(d) / sc, 0, 1) * 3).astype(int)
            for j, v in enumerate(vals):
                sh = 2 * (self.phase * E10B_N + j)
                self.packed = (self.packed & ~(3 << sh)) | (int(v) << sh)
            self.phase = 1 - self.phase
        elif self.kind == "learned_recurrent":
            u = np.clip(d * d / (sc * sc), 0, 1)
            self.z = _e10b_q(np.r_[self.z, u, 1.0] @ self.W)


def _e10b_episode(seed, kind, c, W, ood=False):
    dseq = _e10b_dseq(seed, c, ood)
    x = np.full(E10B_N, c["target"]); st = _e10b_Store(kind, c, W)
    loss = eff = 0.0; traces = []; signs = []
    for d in dseq:
        sal = st.salience(); s = sal.sum()
        alloc = (sal / s if s > 1e-12 else np.full(E10B_N, 1.0 / E10B_N)) * c["action_budget"]
        gain = c["base_gain"] + c["memory_gain"] * alloc
        x = np.clip(x + gain * (c["target"] - x) + d, 0, 1)
        loss += np.mean((x - c["target"]) ** 2)
        eff += np.mean((gain - c["base_gain"]) ** 2)
        st.update(d)
        traces.append(st.salience().copy()); signs.append((d > 0).astype(np.uint8))
    n = c["steps"]
    return dict(loss=loss / n, score=-(loss + 0.08 * eff) / n,
                trace=np.asarray(traces), sign=np.asarray(signs))


def _e10b_ci(d, seed=93, n=5000):
    """IC95% bootstrap pareado (reamostragem das diferenças por semente)."""
    rng = np.random.default_rng(seed)
    z = rng.choice(d, (n, len(d)), replace=True).mean(1)
    return [float(np.quantile(z, .025)), float(np.quantile(z, .975))]


def _e10b_leakage(runs):
    """Decodificador de sinal: metade 1 treina limiar por canal, metade 2 testa."""
    X = np.concatenate([r["trace"] for r in runs])
    Y = np.concatenate([r["sign"] for r in runs]); cut = len(X) // 2
    P = np.zeros_like(Y[cut:])
    for j in range(E10B_N):
        a = X[:cut, j][Y[:cut, j] == 0].mean(); b = X[:cut, j][Y[:cut, j] == 1].mean()
        P[:, j] = (np.abs(X[cut:, j] - b) < np.abs(X[cut:, j] - a))
    return float((P == Y[cut:]).mean())


def e10b_controles(n_seeds=200, train_sequences=None):
    """E10b: resíduo quadrático × 5 memórias fortes, 24 bits cada, ID e OOD.

    Hipótese registrada (MUTARIC ev 2): `square_ema` deve ser comparada a
    magnitude, janela curta e recorrente aprendido — não só à assinada.
    """
    c = dict(E10B_CFG)
    if train_sequences is not None:
        c["train_sequences"] = int(train_sequences)
    W = _e10b_train(c)
    res = {"protocolo": dict(
        config=c, sementes_pareadas=int(n_seeds), bits_mutaveis=E10B_BUDGET,
        treino_recorrente=f"sementes 100000..{100000 + c['train_sequences'] - 1}; "
                          f"avaliacao 50000..; sem sobreposicao",
        hipotese="square_ema deve ser comparada a magnitude, janela curta e "
                 "recorrente aprendido")}
    for split, ood in (("id", False), ("ood", True)):
        raw = {k: [_e10b_episode(50000 + s, k, c, W, ood) for s in range(n_seeds)]
               for k in E10B_KINDS}
        res[split] = {}
        for k, rs in raw.items():
            sc = np.array([r["score"] for r in rs]); lo = np.array([r["loss"] for r in rs])
            res[split][k] = dict(score_medio=float(sc.mean()), loss_medio=float(lo.mean()),
                                 desvio_score=float(sc.std(ddof=1)),
                                 vazamento_sinal=.5 if k == "none" else _e10b_leakage(rs))
        base = np.array([r["score"] for r in raw["square_ema"]])
        res[split]["comparacoes_square_ema"] = {}
        for k in ("magnitude_ema", "short_window", "learned_recurrent"):
            d = base - np.array([r["score"] for r in raw[k]]); ic = _e10b_ci(d, 100 + len(k))
            res[split]["comparacoes_square_ema"][k] = dict(
                delta=float(d.mean()), ic95=ic, vitorias=float((d > 0).mean()),
                conclusao=("favoravel" if ic[0] > 0 else
                           ("desfavoravel" if ic[1] < 0 else "inconclusiva")))
        # vencedor escolhido só depois de todas as métricas registradas
        res[split]["melhor_score"] = max(E10B_KINDS, key=lambda k: res[split][k]["score_medio"])
    res["pesos_recorrentes"] = dict(forma=list(W.shape),
                                    norma_frobenius=float(np.linalg.norm(W)))
    return res


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
    # ---- orçamento igual: resíduo × memória convencional (MUTARIC ev §6, docs/09) ----
    res["E10_orcamento"] = e10_orcamento()
    # ---- controles fortes de memória, 24 bits (auditoria MUTARIC ev 2, docs/10) ----
    res["E10b_controles"] = e10b_controles()

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

    # 9) E10 — orçamento igual: memória convencional × resíduo (docs/09)
    d10 = res["E10_orcamento"]; ags = list(E10_AGENTES); regs = list(d10["J"])
    fig, ax = plt.subplots(2, 2, figsize=(11, 7)); w = 0.35
    cores = ["gray", "tab:orange", "tab:blue", "tab:red"]
    for r, reg in enumerate(regs):
        ax[0, 0].bar(np.arange(4) + (r - 0.5) * w, [d10["J"][reg][a] for a in ags],
                     w, label=f"regime {reg}")
    ax[0, 0].set_xticks(range(4)); ax[0, 0].set_xticklabels(ags)
    ax[0, 0].set_title("J (maior = melhor: −distância + acertos)", fontsize=9)
    ax[0, 0].legend(fontsize=7); ax[0, 0].grid(alpha=.3, axis="y")
    ax[0, 1].bar(range(4), [d10["cond_a_rmse_reconstrucao"][a] for a in ags], 0.6, color=cores)
    ax[0, 1].set_xticks(range(4)); ax[0, 1].set_xticklabels(ags)
    ax[0, 1].set_title("(a) RMSE ao reconstruir o conteúdo (menor = mais conteúdo)", fontsize=9)
    ax[0, 1].grid(alpha=.3, axis="y")
    ax[1, 0].bar(range(4), [d10["cond_b_mi_excesso"][a] for a in ags], 0.6, color=cores)
    ax[1, 0].set_xticks(range(4)); ax[1, 0].set_xticklabels(ags)
    ax[1, 0].axhline(0, color="black", lw=0.8)
    ax[1, 0].set_title("(b) MI excedente com o futuro (bits; abaixo de 0 = só viés)", fontsize=9)
    ax[1, 0].grid(alpha=.3, axis="y")
    for a in ags:
        ax[1, 1].plot(d10["curvas"][regs[0]][a], label=a)
    ax[1, 1].set_title(f"Distância ao alvo, regime {regs[0]} (semente 0)", fontsize=9)
    ax[1, 1].legend(fontsize=7); ax[1, 1].grid(alpha=.3)
    fig.suptitle("E10 — orçamento igual: memória convencional × resíduo (docs/09)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "e10_orcamento.png"), dpi=130); plt.close(fig)

    # 10) E10b — controles fortes de memória, 24 bits (MUTARIC ev 2, docs/10)
    d10b = res["E10b_controles"]; ks = list(E10B_KINDS)
    rot = ["sem\nmemória", "EMA\nassinada", "EMA\nmagnitude", "resíduo\nquadrático",
           "janela\ncurta", "recorrente\naprendido"]
    cores = ["gray", "tab:orange", "tab:green", "tab:red", "tab:blue", "tab:purple"]
    fig, ax = plt.subplots(2, 2, figsize=(11, 7))
    for col, split in enumerate(("id", "ood")):
        ax[0, col].bar(range(6), [d10b[split][k]["score_medio"] for k in ks], color=cores)
        ax[0, col].set_xticks(range(6)); ax[0, col].set_xticklabels(rot, fontsize=7)
        ax[0, col].set_title(f"score {'ID' if split == 'id' else 'OOD'} (maior = melhor)",
                             fontsize=9)
        ax[0, col].grid(alpha=.3, axis="y")
        cs = d10b[split]["comparacoes_square_ema"]; ck = list(cs)
        meio = [cs[k]["delta"] for k in ck]
        err = [[cs[k]["delta"] - cs[k]["ic95"][0] for k in ck],
               [cs[k]["ic95"][1] - cs[k]["delta"] for k in ck]]
        ax[1, col].barh(range(3), meio, xerr=err, color="tab:red", height=.5)
        ax[1, col].axvline(0, color="black", lw=.8)
        ax[1, col].set_yticks(range(3)); ax[1, col].set_yticklabels(ck, fontsize=7)
        ax[1, col].set_title("Δ pareado: resíduo − controle (IC95%)", fontsize=9)
        ax[1, col].grid(alpha=.3, axis="x")
    fig.suptitle("E10b — controles fortes de memória, 24 bits por agente (docs/10)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "e10b_controles.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    if "--telemetria" in sys.argv:
        print(json.dumps(coleta_telemetria(), indent=1, ensure_ascii=False, default=str))
    else:
        main()
