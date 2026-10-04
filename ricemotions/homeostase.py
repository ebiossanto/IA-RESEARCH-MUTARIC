"""
Homeostase — o que do documento MutaCore/RIC está correto e entra no trabalho.

Análise, vereditos e provas: ``docs/06_analise_mutacore.md``. Aqui ficam só os
mecanismos que passaram na análise, todos PUROS (só numpy, sem I/O, determinísticos)
para poderem ser testados. A única exceção é :func:`telemetria`, opcional e nunca
usada por teste ou experimento (leitura de hardware é não-determinística).

Quatro mecanismos, com a origem e o veredito:

1. ``residuo_transicao`` / ``sensibilidade`` / ``injetar``  (MutaCore §B)
   Resíduo ENDÓGENO — a energia da transição do próprio estado,
   ``ΔH_L(t) = γ·Σ QW_i·|X_i(t) − X_i(t−1)|²``, acumulado em ``R_L`` e injetado
   de volta por ``Φ(R_L)``. Diferença para :func:`ricemotions.residuo.gerar`: aqui
   o resíduo vem do que o sistema FEZ (procedência da transição), não de um sorteio.
   Veredito: reproduz o JSON publicado integralmente (E7), mas o deslocamento máximo
   é |Φ| ≈ 0,021 numa escala [0,1] — numericamente inerte nos parâmetros publicados.

2. ``fator_termico`` / ``S_star_homeostatico`` / ``tau_carga``  (MutaCore §C)
   Telemetria -> alvo S* e limiar τ. A telemetria chega como ARGUMENTO puro;
   quem mede é o chamador. Veredito: correto e incorporado —
   ``Agente.passo(..., carga_hw=...)`` sobe o τ do RIC com a carga da máquina.

3. ``politica``  (MutaCore §D)
   DEFENSIVA/EXPLORATORIA pela distância ao S*. Veredito: correto; no benchmark
   é ESTA política (recarregar cedo) que muda a sobrevivência, não S* (E8, ablação).

4. ``passo_robo``  (MutaCore §E)
   Um passo do robô do benchmark de sobrevivência (1000 ciclos).
   Veredito: nos parâmetros publicados a morte é IMPOSSÍVEL (E8); em regime letal
   o S* dinâmico REDUZ a sobrevivência em relação ao S* fixo.
"""
import numpy as np

from ricemotions.mundo import S_STAR, NV, QW

# parâmetros do JSON publicado no documento (γ=0.8, α_L=0.15, λ do 2º código)
GAMMA, ALPHA_L = 0.8, 0.15
LAMBDAS = np.array([-0.25, 0.35, -0.4, 0.0, -0.15, 0.2])

# o JSON que o documento afirma ter obtido — E7 e o teste o reproduzem
PUBLICADO = {
    "alegria-meta":    dict(max_residual_stress=0.029968, final_tension_diff=0.002241,
                            final_coherence_drop=0.000004),
    "alegria-vínculo": dict(max_residual_stress=0.010617, final_tension_diff=0.000977,
                            final_coherence_drop=0.000001),
    "alegria-estado":  dict(max_residual_stress=0.0, final_tension_diff=0.0,
                            final_coherence_drop=0.0),
    "tristeza-meta":   dict(max_residual_stress=0.026211, final_tension_diff=0.001988,
                            final_coherence_drop=0.000003),
    "tristeza-vínculo": dict(max_residual_stress=0.019202, final_tension_diff=0.001628,
                             final_coherence_drop=0.000002),
    "tristeza-estado": dict(max_residual_stress=0.0, final_tension_diff=0.0,
                            final_coherence_drop=0.0),
}


# ---------------------------------------------------------------- 1. resíduo
def residuo_transicao(X, gamma=GAMMA, alpha=ALPHA_L, qw=None):
    """R_L(t) da MutaCore §B: energia da TRANSIÇÃO do próprio estado.

    ``ΔH_L(t) = γ·Σ QW_i·|X_i(t) − X_i(t−1)|²`` (t ≈ t−1) acumulado com resfriamento
    ``R_L(t) = (1−α)·R_L(t−1) + ΔH_L(t)``. Devolve ``R_L`` com ``R_L[0] = 0``,
    forma ``(T,)`` de ``X`` (NV, T).
    """
    X = np.asarray(X, float)
    w = QW if qw is None else np.asarray(qw, float)
    dH = gamma * (w[:, None] * np.diff(X, axis=1) ** 2).sum(0)      # (T-1,)
    R = np.zeros(X.shape[1])
    for i, h in enumerate(dH):
        R[i + 1] = (1.0 - alpha) * R[i] + h
    return R


def sensibilidade(R, lambdas=LAMBDAS):
    """Φ(R_L) — vetor de sensibilidade afetiva (MutaCore §B).

    Aceita escalar (devolve ``(NV,)``) ou trajetória (devolve ``(NV, T)``).
    B (vínculo) é invariante por construção; os sinais vêm de LAMBDAS.
    """
    R = np.asarray(R, float)
    L = np.asarray(lambdas, float)
    out = np.zeros((NV,) + R.shape)
    out[0] = L[0] * R
    out[1] = L[1] * np.tanh(2.0 * R)
    out[2] = L[2] * R ** 2
    out[4] = L[4] * R
    out[5] = L[5] * np.log1p(R)
    return out


def injetar(X, R=None, lambdas=LAMBDAS):
    """X + Φ(R_L), recortado em [0,1] — a injeção do MutaCore §B."""
    X = np.asarray(X, float)
    R = residuo_transicao(X) if R is None else R
    return np.clip(X + sensibilidade(R, lambdas), 0.0, 1.0)


def roteiro_mutacore(fam, cause, t0=14):
    """O episódio DETERMINÍSTICO do documento (sem ruído, sem sorteio de base).

    Só existe para reproduzir o JSON publicado — ver E7. O roteiro usado no
    trabalho continua a ser :func:`ricemotions.mundo.episode`.
    """
    T = 32
    t = np.arange(T)
    f = 1 if fam == "alegria" else -1
    b = np.array([0.7, 0.35, 0.75, 0.5, 0.35, 0.4])

    def rise(u, tau):
        return (u >= t0) * (1.0 - np.exp(-(u - t0) / tau))

    def pulse(u, tau):
        d = (u - t0) / tau
        return (u >= t0) * d * np.exp(1.0 - d)

    def ramp(a, bb):
        return np.clip((t - a) / max(bb - a, 1), 0, 1)

    X = np.tile(b[:, None], (1, T)).astype(float)
    if cause == "meta":
        X[0] -= 0.18 * ramp(3, t0)
        X[1] += 0.15 * ramp(3, t0)
        if f > 0:
            X[4] += 0.85 * (0.8 - X[4, t0 - 1]) * rise(t, 2.0)
            X[1] += 0.85 * (0.25 - X[1, t0 - 1]) * rise(t, 2.0)
            X[2] += 0.6 * (0.9 - X[2, t0 - 1]) * rise(t, 3.0)
        else:
            X[4] -= 0.30 * rise(t, 2.0)
            X[1] += 0.25 * rise(t, 2.0)
            X[2] -= 0.20 * rise(t, 3.0)
    elif cause == "vínculo":
        if f > 0:
            X[3] += 0.85 * (0.7 - X[3, t0 - 1]) * rise(t, 2.5)
            X[2] += 0.6 * (0.9 - X[2, t0 - 1]) * rise(t, 3.0)
            X[5] += 0.20 * pulse(t, 3.0)
        else:
            X[3] -= 0.40 * rise(t, 2.5)
            X[2] -= 0.15 * rise(t, 3.0)
    return np.clip(X, 0, 1)


def simular_landauer(gamma=GAMMA, alpha=ALPHA_L, lambdas=LAMBDAS):
    """Aplica o loop completo ao roteiro determinístico. Devolve {classe: métricas}
    no MESMO formato do JSON publicado + a magnitude de Φ."""
    out, max_phi = {}, 0.0
    from ricemotions.mundo import CLASSES, FAMILIAS, CAUSAS
    for fam in FAMILIAS:
        for cause in CAUSAS:
            Xb = roteiro_mutacore(fam, cause)
            R = residuo_transicao(Xb, gamma=gamma, alpha=alpha)
            phi = sensibilidade(R, lambdas)
            Xd = np.clip(Xb + phi, 0.0, 1.0)
            max_phi = max(max_phi, float(np.abs(phi).max()))
            out[f"{fam}-{cause}"] = dict(
                max_residual_stress=float(R.max()),
                final_tension_diff=float(Xd[1, -1] - Xb[1, -1]),
                final_coherence_drop=float(Xb[2, -1] - Xd[2, -1]))
    out["_max_phi"] = max_phi
    return out


# --------------------------------------------------- 2. homeostase de hardware
def fator_termico(temp_c, t0=40.0, t1=80.0):
    """Normaliza a temperatura em estresse térmico [0,1] (MutaCore §C)."""
    return float(np.clip((float(temp_c) - t0) / (t1 - t0), 0.0, 1.0))


def S_star_homeostatico(temp_c=40.0, ram=0.0, base=None):
    """Alvo S* adaptado pela telemetria da máquina (MutaCore §C, regras 1).

    Térmico puxa E para baixo (aceita cansaço), RAM alta sobe o teto de T,
    térmico degrada C e G e joga N para cima (alerta). B não muda.
    Devolve recortado em [0,1] — ver docs/06 §8 para por que isso importa.
    """
    tf = fator_termico(temp_c)
    s = (S_STAR if base is None else np.asarray(base, float)).copy()
    s[0] -= 0.35 * tf
    s[1] += 0.40 * float(ram) ** 2
    s[2] -= 0.30 * tf ** 2
    s[4] -= 0.25 * tf
    s[5] += 0.30 * np.log1p(tf)
    return np.clip(s, 0.0, 1.0)


def tau_carga(thermal=0.0, cpu=0.0, amplitude=0.15):
    """Termo ADITIVO de τ vindo da carga da máquina (MutaCore §C, regra 2).

    ``amplitude·(térmico + cpu)/2`` ∈ [0, amplitude]. Soma-se ao τ que já vem do
    resíduo (``residuo.tau_efetivo``), não o substitui.
    """
    return float(amplitude * (np.clip(float(thermal), 0, 1) + np.clip(float(cpu), 0, 1)) / 2.0)


def politica(X, s_star, limiar_t=0.15, limiar_e=0.25):
    """DEFENSIVA se tensão acima do alvo OU déficit de energia; senão EXPLORATORIA.

    É uma função do DISTANCIMENTO ao S* — não um limiar fixo em E (MutaCore §D).
    """
    X = np.asarray(X, float)
    s = np.asarray(s_star, float)
    tenso = (X[1] - s[1] > limiar_t) or (s[0] - X[0] > limiar_e)
    return "DEFENSIVA" if tenso else "EXPLORATORIA"


# ------------------------------------------------------- 4. robô do benchmark
def passo_robo(X, env_noise, cpu_stress, dinamico=True, generosa=True,
               esfria=0.10, gasto=0.015, carga=0.12, rng=None, s_star=None):
    """Um passo do robô simulado do benchmark MutaCore (docs/06 §4).

    Devolve ``(X, vivo, defensiva, meta)`` — ``meta`` diz se houve exploração
    bem-sucedida neste passo (só acontece fora da política defensiva, como no
    documento). Os três interruptores separam o que o documento mistura num só
    rótulo "afetivo":

    ``dinamico``  S* se move com a tensão (S*_E −= 0,35·tf; S*_T += 0,30·tf)
    ``generosa``  política pelo DISTANCIMENTO ao S* vs limiar fixo E < 0,20
    ``esfria``    quanto a política DEFENSIVA baixa a tensão por ciclo
    """
    X = np.asarray(X, float).copy()
    cpu = 0.8 if cpu_stress else 0.2
    dH = 0.15 * cpu ** 2 + 0.05 * float(env_noise)
    X[0] -= gasto
    X[1] = 0.85 * X[1] + dH
    X[2] = 0.90 * X[2] - 0.02 * float(env_noise)

    s = (S_STAR if s_star is None else np.asarray(s_star, float)).copy()
    if dinamico:
        tf = np.clip((X[1] - 0.2) / 0.6, 0.0, 1.0)
        s[0] -= 0.35 * tf
        s[1] += 0.30 * tf
        s[4] -= 0.25 * tf
    if generosa:
        defensiva = politica(X, s) == "DEFENSIVA"
    else:
        defensiva = bool(X[0] < 0.20)

    if defensiva:
        X[0] += carga
        X[1] -= esfria
        meta = False
    elif rng is not None and rng.random() < 0.25:
        X[4] = min(1.0, X[4] + 0.15)
        meta = True
    else:
        meta = False

    X = np.clip(X, 0.0, 1.0)
    vivo = not (X[0] <= 0.0 or X[1] >= 0.95)
    return X, vivo, defensiva, meta


# ------------------------------------------------------------ telemetria opcional
def telemetria():
    """``(cpu, ram, temp_C)`` da máquina REAL, ou ``None`` se psutil faltar.

    Nunca usada por teste nem por experimento: leitura de hardware é
    não-determinística e isso quebraria a reprodutibilidade do trabalho.
    Correções sobre o código do documento: a primeira chamada de
    ``cpu_percent(interval=None)`` devolve 0,0 (descartada); sem sensor térmico
    a temperatura é MODELADA, não medida, e isso é declarado aqui.
    """
    try:
        import psutil
    except Exception:
        return None
    psutil.cpu_percent(interval=None)                    # primeira amostra: 0,0
    cpu = float(psutil.cpu_percent(interval=0.1)) / 100.0
    ram = float(psutil.virtual_memory().percent) / 100.0
    temp = None
    sensores = getattr(psutil, "sensors_temperatures", None)
    if callable(sensores):
        try:
            for nome in ("coretemp", "cpu_thermal"):
                lst = sensores().get(nome)
                if lst:
                    temp = float(lst[0].current)
                    break
        except Exception:
            temp = None
    if temp is None:
        temp = 35.0 + 50.0 * (cpu ** 2)                  # MODELO, não medição
    return cpu, ram, temp
