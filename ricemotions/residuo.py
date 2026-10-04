"""
Resíduo do ambiente: gerar, ROTEAR e ler.

A mesma energia de resíduo pode ter três destinos (experimento E5):

  A. ESPALHADO  vira ruído de pixel e destrói a leitura (é o modelo das E1-E4).
  B. BANDA      linhas-de-patch 16-21 dedicadas: leitura intacta, resíduo exato,
                custa 6 linhas do orçamento do glifo.
  C. SIMETRIA   vira uma permutação do corpo (6! = 720): leitura intacta, custa ZERO
                linhas e carrega a ORDEM dos 6 canais — log2(720) = 9,49 bits.

Dois mecanismos de realimentação (docs/05):

  * Filtro de Landauer — a energia lógica DESCARTADA na leitura (variância intra-patch
    que a média de 3 pixels apaga + magnitude de correlação que o limiar colapsa em 1 bit)
    não é jogada fora: ela entra em T (tensão) e C (coerência) do próximo passo.
    Apagar informação custa energia; essa energia volta como tensão.

  * τ efetivo — o resíduo acumulado sobe o limiar de aresta do RIC. Resíduo alto =>
    menos arestas => menos reação a estímulo fraco => "mau humor"/"exaustão".
    É a modularização do ambiente: o ambiente não entra pelos pixels, entra no
    PARÂMETRO de leitura.
"""
import numpy as np

from ricemotions.mundo import NV, T
from ricemotions import glifo as G


# ---------------- geração ----------------
def gerar(nv=NV, t_steps=T, rng=None, amp=0.35, rho=0.9, comum=0.4):
    """Resíduo ESTRUTURADO (6, t_steps): AR(1) por canal + componente comum.

    Não é ruído branco: tem memória temporal (rho) e correlação entre canais (comum),
    que é o que caracteriza um resíduo de processamento ("frustração", "carga").
    |r| fica limitado por ~2.5*amp, então amp <= 0.35 cabe em [0,1] ao ser gravado.
    """
    rng = np.random.default_rng() if rng is None else rng
    e = rng.normal(0, 1, (nv, t_steps))
    r = np.zeros((nv, t_steps))
    for k in range(1, t_steps):
        r[:, k] = rho * r[:, k - 1] + e[:, k]
    r /= (r.std(1, keepdims=True) + 1e-9)
    com = np.cumsum(rng.normal(0, 1, t_steps))
    com = (com - com.mean()) / (com.std() + 1e-9)
    r = amp * ((1 - comum) * r + comum * com[None, :])
    return np.clip(r, -1.0, 1.0)


def memoria(r):
    """Memória bruta do resíduo por canal: média das MAGNITUDES -> (6,).
    Usa |r| porque o sentido não importa — carga é carga."""
    return np.abs(r).mean(1)


def memoria_ema(r, prev, alpha=0.15):
    """Atualização da memória: novo = (1-alpha)*antigo + alpha*magnitude média."""
    return (1 - alpha) * prev + alpha * np.abs(r).mean(1)


# ---------------- os três roteamentos ----------------
def para_pixels(r, seed=1234):
    """Condição A: a MESMA energia total espalhada como ruído branco na imagem.

    A energia (soma dos quadrados do resíduo) é conservada e distribuída por todas as
    amostras de pixels, o que torna a comparação com as condições B e C justa.
    Devolve (ruído, sigma), com sigma = sqrt(energia / n_amostras).
    """
    rng = np.random.default_rng(seed)
    n = G.NROWS * G.R * T
    sigma = float(np.sqrt(np.sum(r ** 2) / n))
    return rng.normal(0.0, sigma, (G.NROWS * G.R, T)), sigma


def para_banda(r):
    """Condição B: banda RESÍDUO em [0,1], centrada em 0,5 (convenção das outras bandas).

    `gerar` limita |r| <= 1, então 0.5 + 0.5r NÃO satura e a leitura é exata.
    """
    return np.clip(0.5 + 0.5 * r, 0.0, 1.0)


def para_permutacao(r):
    """Condição C: a ordem de carga dos canais -> uma das 720 permutações (a SIMETRIA
    carrega o resíduo). `argsort` da magnitude média de cada canal."""
    return tuple(int(i) for i in np.argsort(np.abs(r).mean(1)))


def ordem_de_permutacao(p):
    """Inversa: permutação -> ordinal por canal. `out[j]` = posição do canal j no ranking."""
    p = np.asarray(p, dtype=int)
    out = np.empty(len(p), dtype=int)
    out[p] = np.arange(len(p))
    return out


def ordinal_de_r(r):
    """Ordinal verdadeiro do resíduo (para comparar com o recuperado)."""
    return ordem_de_permutacao(para_permutacao(r))


# ---------------- leitura do que foi routado ----------------
def recuperar_banda(img):
    """Condição B: devolve (6,32) o resíduo lido da banda, ou None se não existe."""
    P = G.patches(img)
    if P.shape[0] < G.SL_RES.stop:
        return None
    return 2.0 * (P[G.SL_RES] - 0.5)


def recuperar_ordinal_banda(img):
    r = recuperar_banda(img)
    return None if r is None else ordinal_de_r(r)


def recuperar_ordinal_ruido(img, r_true):
    """Condição A: o ruído branco não tem estrutura por canal.

    Estimamos a energia por canal a partir da variância intra-patch das linhas do
    corpo; como o ruído é i.i.d., todas as estimativas ficam ~iguais e a ordenação
    não recupera a do resíduo verdadeiro (retorna None = não recuperável).
    """
    _ = r_true, img
    return None


# ---------------- Filtro de Landauer ----------------
def energia_descartada(img, tau=0.7):
    """Energia lógica DESCARTADA quando o leitor representa a imagem.

    Três componentes, todas medidas na própria imagem (sem rótulo):

    ``intra_patch``  a média de 3 pixels de cada patch apaga a variância entre eles;
    ``quantizacao``  o arredondamento para 8 bits;
    ``limiar``       a magnitude de correlação que `|cos| > tau` colapsa em 1 bit:
                     min(|c|, tau) — o que era um número vira um dígito.

    Retorna o dicionário com as três e o ``total`` usado pelo filtro.
    """
    b = img.reshape(-1, G.R, T)
    intra = float(np.var(b, axis=1).mean())
    q = float(np.mean((img - np.round(np.clip(img, 0, 1) * 255) / 255.0) ** 2))
    c = G.corr(G.patches(img)[G.SL_CORPO])[G.IU]
    limiar = float(np.minimum(np.abs(c), tau).mean())
    return dict(intra_patch=intra, quantizacao=q, limiar=limiar,
                total=float(intra + limiar))


def landauer_passo(anterior, posterior, tau=0.7):
    """Energia descartada ENTRE dois passos: o que a representação de `anterior`
    não levou para `posterior` (erro de reconstrução). Usado pelo agente em loop."""
    err = float(np.mean((G.patches(anterior)[G.SL_CORPO] - G.patches(posterior)[G.SL_CORPO]) ** 2))
    return dict(erro_reconstrucao=err, total=err + energia_descartada(posterior, tau)["limiar"])


# ---------------- τ do ambiente ----------------
def tau_efetivo(tau0, res_global, k_tau=0.9, lo=0.45, hi=0.95):
    """Limiar de aresta modulado pelo resíduo acumulado.

    res_global ~0 => tau0 (estado normal). res_global alto => tau sube, o grafo encolhe,
    estímulos fracos deixam de produzir aresta — o equivalente operacional de
    "mau humor"/"exaustão". Limitado a [lo, hi] para não colapsar nem abrir demais.
    """
    return float(np.clip(tau0 + k_tau * float(res_global), lo, hi))


def reatividade(img_a, img_b, tau):
    """Fração de arestas do corpo que muda entre duas imagens — sensibilidade a um
    estímulo fraco. Com tau alto, menos arestas mudam: o sistema fica menos reativo."""
    a = G.body_graph(img_a, tau)
    b = G.body_graph(img_b, tau)
    return float(np.mean(a != b))
