"""
Agência — a mão dupla entre o estado emocional e as regras de transição.

Comparação com `mundo.py`:

  mundo.episode()   ROTEIRO: a causa externa escreve o perfil de resposta.
                    Nada é decidido, nada realimenta nada (ver o aviso no arquivo).
  agente.Agente()   SISTEMA DINÂMICO: existe uma transição X -> X' e o que é LIDO
                    do próprio estado altera as PRÓPRRIAS regras dessa transição.

Três realimentações (docs/05):

  1. Filtro de Landauer  a energia descartada na representação (variância que a média
                         de 3 pixels apaga + magnitude que o limiar colapsa em 1 bit)
                         entra em T (sobe) e C (desce) do próximo passo.
  2. Memória de resíduo  o resíduo acumulado sobe o limiar tau do RIC (menos arestas,
                         menos reação a estímulo fraco = "mau humor"/"exaustão") e
                         repondera os pesos w (postura mais rígida/defensiva).
  3. S* temporário       o alvo muda com a tensão e RELAXA de volta — mudança
                         temporária, não troca de identidade.

Critério operacional de agência que E6 mede:

  DOIS agentes no MESMO estado X, com histórias de resíduo diferentes, produzem
  transições DIFERENTES. Em modo aberto a diferença é exatamente 0 — é esse 0 que
  separa "roteiro" de "mão dupla".
"""
import numpy as np

from ricemotions.mundo import NV, T, affect
from ricemotions import glifo as G
from ricemotions import residuo as R

# acoplamento fixo entre canais (E,T,C,B,G,N) — o ambiente interno não é independente:
# tensão pressiona energia, coerência inibe tensão, progresso acalma tensão, etc.
J = 0.12 * np.array([
    [0, -1, 0, 0, 0, 1],
    [1, 0, -1, 0, 0, 0],
    [0, 1, 0, -1, 1, 0],
    [0, 0, 1, 0, 0, -1],
    [0, 0, -1, 0, 0, 1],
    [-1, 0, 0, 1, -1, 0]], float)

PADRAO = (0, 0, 1, 1, 2, 2)          # carga fixa do auto-retrato (não participa de E6)


def transicao(X, s_star, w, rng, dt=0.30, ruido=0.004):
    """Um passo: relaxação dirigida ao ALVO + acoplamento entre canais + ruído.

    `s_star` e `w` vêm do agente — é por isso que mudar o estado muda a regra.
    """
    X = np.asarray(X, float)
    drift = np.asarray(w, float) * (np.asarray(s_star, float) - X)
    coupl = J @ np.tanh(2.0 * (X - 0.5))
    return np.clip(X + dt * (drift + coupl) + rng.normal(0, ruido, X.shape), 0, 1)


class Agente:
    """Estado X, alvo S*, pesos w, memória de resíduo e limiar tau — todos acoplados."""

    def __init__(self, s_star, tau0=0.7, fechado=True, landauer=True,
                 k_t=0.025, k_c=0.025, k_tau=0.5, k_w=0.8, beta_t=0.3,
                 alpha=0.15, k_relax=0.06, seed=0):
        # `fechado=False` é o experimento de controle (mão única): regras fixas.
        self.s0 = np.asarray(s_star, float).copy()
        self.s = self.s0.copy()
        self.w = np.ones(NV)
        self.res = np.zeros(NV)
        self.tau0, self.tau = tau0, tau0
        self.fechado, self.landauer = fechado, landauer
        self.k_t, self.k_c = k_t, k_c
        self.k_tau, self.k_w, self.beta_t = k_tau, k_w, beta_t
        self.alpha, self.k_relax = alpha, k_relax
        self.rng = np.random.default_rng(seed)
        self.hist = []                                   # trajetória recente (auto-retrato)
        self.log = {"s_T": [], "s_C": [], "tau": [], "w": [], "landauer": [], "res": []}

    # ---- percepção ----
    def representar(self, X):
        """Escreve o próprio estado como glifo — a representação é o que PERDE informação.
        O CORPO é a TRAJETÓRIA dos últimos T passos (não um estado isolado)."""
        X = np.asarray(X, float)
        self.hist.append(X.copy())
        H = np.array(self.hist[-T:])
        if len(H) < T:
            H = np.vstack([np.repeat(H[:1], T - len(H), 0), H])
        seq = H.T                                                    # (NV, T)
        v, a = affect(seq)
        fam = "alegria" if v > 0 else "tristeza"
        return G.render(seq, v, a, fam, PADRAO, self.rng)

    def perceber(self, img, residuo_atual=None):
        """Mede a energia descartada (Landauer) e atualiza a memória de resíduo."""
        E = R.energia_descartada(img, self.tau)["total"]
        if residuo_atual is not None:
            self.res = R.memoria_ema(residuo_atual, self.res, self.alpha)
        return E

    # ---- mão dupla ----
    def modular(self, E, X):
        """Aqui o estado altera as PRÓPRRIAS regras. Em modo aberto, não faz nada."""
        if not self.fechado:
            return 0.0
        # 1) Landauer: informação apagada vira tensão (+) e custa coerência (-)
        if self.landauer and E > 0:
            self.s[1] = np.clip(self.s[1] + self.k_t * E, 0, 1)
            self.s[2] = np.clip(self.s[2] - self.k_c * E, 0, 1)
        # relaxamento: o alvo muda TEMPORARIAMENTE e volta (S* não é trocado)
        self.s = self.s0 + (self.s - self.s0) * (1.0 - self.k_relax)
        # 2) resíduo acumulado + tensão acima do normal -> tau e pesos
        g = float(self.res.mean())
        tensao_excedente = max(0.0, float(X[1]) - float(self.s0[1]))
        self.tau = R.tau_efetivo(self.tau0, g + self.beta_t * tensao_excedente,
                                 self.k_tau)
        self.w = np.clip(1.0 + self.k_w * (self.res - g), 0.3, 2.0)
        return g

    # ---- ciclo ----
    def passo(self, X, residuo_atual=None):
        img = self.representar(X)
        E = self.perceber(img, residuo_atual)
        g = self.modular(E, X)
        Xn = transicao(X, self.s, self.w, self.rng)
        self.log["s_T"].append(float(self.s[1])); self.log["s_C"].append(float(self.s[2]))
        self.log["tau"].append(float(self.tau)); self.log["w"].append(self.w.copy())
        self.log["landauer"].append(float(E)); self.log["res"].append(float(g))
        return Xn

    def regras(self):
        """(s*, w, tau) — o estado atual das regras de transição."""
        return self.s.copy(), self.w.copy(), self.tau


def criterio_mao_dupla(X, ag, res_alto=0.3):
    """Núcleo de E6: mesmo estado X, histórico de resíduo diferente -> próxima transição?

    `res_alto` aceita escalar ou vetor (6,); o caso real é POR CANAL, e é o vetor que
    diferencia os pesos w de um canal para outro.

    Devolve a distância entre a próxima transição com resíduo e com resíduo nulo (sem
    ruído, para isolar a REGRA), além dos dois taus.

    Em modo aberto a distância é 0 exato — a regra é função só de X. Esse 0 é o que
    separa "roteiro" de "mão dupla".
    """
    alto = np.full(NV, res_alto, float) if np.isscalar(res_alto) else np.asarray(res_alto, float)
    nulo = np.zeros(NV)

    def _proximo(res):
        # snapshots: as duas chamadas partem do MESMO estado interno, para que a
        # única diferença seja o resíduo (senão a relaxação de s contamina o teste)
        s0_, w0_, t0_, r0_ = ag.s.copy(), ag.w.copy(), ag.tau, ag.res.copy()
        ag.res = res.copy()
        ag.modular(0.0, X)
        nxt = X + 0.30 * (ag.w * (ag.s - X)) + 0.30 * (J @ np.tanh(2.0 * (X - 0.5)))
        out = nxt, ag.tau
        ag.s, ag.w, ag.tau, ag.res = s0_, w0_, t0_, r0_
        return out

    alta, tau_alta = _proximo(alto)
    nula, tau_nula = _proximo(nulo)
    ag.res = np.zeros(NV)
    ag.modular(0.0, X)
    return float(np.mean(np.abs(alta - nula))), tau_alta, tau_nula
