"""
Mundo afetivo — gera episódios de 32 passos sobre seis canais internos e os rotula por
(FAMÍLIA afetiva) x (PROCEDÊNCIA).

Canais (linhas): E energia, T tensão, C coerência, B vínculo, G progresso de meta, N novidade.
Família:      alegria | tristeza        (sinal da valência: aproximação/afastamento do alvo s*)
Procedência:  meta | vínculo | estado   (de onde veio a mudança)

  alegria-meta     ter ganhado: esforço (E cai, T sobe) -> meta alcançada: G sobe, T descarrega, C sobe
  alegria-vínculo  encontrar um amigo: B sobe, C sobe, T desce devagar, pulso de novidade; sem esforço
  alegria-estado   estar tudo bem: perto do alvo, quase nada se move
  tristeza-meta    fracasso: mesmo esforço, mas G cai e T sobe
  tristeza-vínculo perda: B cai, C cai, T sobe devagar, N cai
  tristeza-estado  mal-estar difuso: E,C,N,B descem e T sobe, todos juntos, lentamente

AVISO: as procedências são ROTEIROS que eu construí (causa externa -> perfil de resposta). O que se
testa depois é o CÓDIGO (como a procedência aparece nas relações entre canais), não a emergência da
procedência a partir de um agente.
"""
import numpy as np

VARS = ["E", "T", "C", "B", "G", "N"]
NV, T = 6, 32
S_STAR = np.array([0.8, 0.25, 0.9, 0.7, 0.8, 0.4])
QW = np.array([1.0, 1.0, 0.5, 1.0, 1.0, 0.5])
FAMILIAS = ["alegria", "tristeza"]
CAUSAS = ["meta", "vínculo", "estado"]
CLASSES = [(f, c) for f in FAMILIAS for c in CAUSAS]


def rise(t, t0, tau): return (t >= t0) * (1 - np.exp(-(t - t0) / tau))
def pulse(t, t0, tau):
    d = (t - t0) / tau
    return (t >= t0) * d * np.exp(1 - d)
def ramp(t, a, b): return np.clip((t - a) / max(b - a, 1), 0, 1)


def dist(X):
    """X: (NV, T) -> distância ponderada ao alvo em cada passo."""
    return np.sqrt((QW[:, None] * (X - S_STAR[:, None]) ** 2).sum(0))


def episode(fam, cause, rng, noise=0.015):
    t = np.arange(T)
    f = 1 if fam == "alegria" else -1
    a = rng.uniform(0.7, 1.3)
    t0 = int(rng.integers(12, 18))
    j = lambda: rng.uniform(-1, 1)
    if cause == "estado" and f > 0:
        b = S_STAR + rng.normal(0, 0.05, NV)
    else:
        b = rng.uniform([0.5, 0.2, 0.6, 0.3, 0.2, 0.2], [0.9, 0.5, 0.9, 0.7, 0.5, 0.6])
    X = np.tile(b[:, None], (1, T)).astype(float)
    if cause == "meta":
        X[0] -= 0.18 * a * ramp(t, 3, t0)
        X[1] += 0.15 * a * ramp(t, 3, t0)
        if f > 0:                                   # alegria = APROXIMAÇÃO do alvo (fração da distância)
            for i, frac, tau in [(4, 0.85, 2), (1, 0.85, 2), (2, 0.6, 3)]:
                X[i] += frac * min(a, 1.15) * (S_STAR[i] - X[i, t0 - 1]) * rise(t, t0 + j(), tau)
        else:
            X[4] -= 0.30 * a * rise(t, t0 + j(), 2)
            X[1] += 0.25 * a * rise(t, t0 + j(), 2)
            X[2] -= 0.20 * a * rise(t, t0 + j(), 3)
    elif cause == "vínculo":
        if f > 0:
            for i, frac, tau in [(3, 0.85, 2.5), (2, 0.6, 3), (1, 0.6, 5)]:
                X[i] += frac * min(a, 1.15) * (S_STAR[i] - X[i, t0 - 1]) * rise(t, t0 + j(), tau)
            X[5] += 0.20 * a * pulse(t, t0 + j(), 3)
            X[0] += 0.06 * a * rise(t, t0, 8)
        else:
            X[3] -= 0.40 * a * rise(t, t0 + j(), 2.5)
            X[2] -= 0.15 * a * rise(t, t0 + j(), 3)
            X[1] += 0.20 * a * rise(t, t0 + j(), 5)
            X[5] -= 0.10 * a * pulse(t, t0 + j(), 3)
            X[0] -= 0.06 * a * rise(t, t0, 8)
    else:
        if f < 0:
            for i, amp in [(0, -0.25), (1, 0.25), (2, -0.20), (5, -0.15), (3, -0.10)]:
                X[i] += amp * a * ramp(t, 0, T)
    if rng.random() < 0.3:                                   # distrator espúrio
        i = rng.integers(NV)
        X[i] += rng.choice([-1, 1]) * 0.10 * pulse(t, rng.integers(4, 28), 3)
    X += rng.normal(0, noise, X.shape)
    return np.clip(X, 0, 1)


def affect(X, alpha=0.3, beta=2.0, d_ref=0.5):
    """valência v (mesma ideia do TEOA: nível -D e taxa L) e ativação."""
    d = dist(X)
    D_pre, D_post = d[:8].mean(), d[-8:].mean()
    L = D_pre - D_post
    v = beta * L - alpha * (D_post - d_ref)
    act = float(np.clip(np.abs(np.diff(d)).mean() * 12, 0, 1))
    return float(v), act


def make_set(n_per_class, seed):
    rng = np.random.default_rng(seed)
    eps, labs = [], []
    for k, (f, c) in enumerate(CLASSES):
        for _ in range(n_per_class):
            eps.append(episode(f, c, rng)); labs.append(k)
    return eps, np.array(labs)
