"""
Glifo emocional — a emoção escrita em PIXELS, lida pelo RIC (incidência relacional).

Imagem (16 linhas-de-patch x 32 colunas; cada linha-de-patch = R=3 linhas de pixels):
  linhas 0-1   NÍVEL      valência e ativação como intensidade (canal de ESTADO, quebra com ganho)
  linhas 2-3   POLARIDADE par de linhas: iguais => alegria, invertidas => tristeza (canal RELACIONAL do afeto)
  linhas 4-9   CORPO      os 6 canais internos (E,T,C,B,G,N) ao longo do tempo (procedência INTRÍNSECA)
  linhas 10-15 CARGA      mensagem EXPLÍCITA: partição das 6 linhas em blocos que compartilham portadora
                          (procedência/qualquer conteúdo, estilo RIC: símbolo = grafo-alvo)
  linhas 16-21 RESÍDUO    (OPCIONAL) banda dedicada: o resíduo do ambiente escrito como ESTRUTURA,
                          em vez de espalhado como ruído nos pixels — ver docs/05.

Leitura (RIC): patch = linha; feature = linha centrada e normalizada (cosseno = correlação);
aresta se |cos| > tau; decodificação por menor distância de incidência d_I (Hamming de arestas).
Diferença para o RIC original (documentada): centramos a feature; sem isso todo cosseno de sinais
positivos é alto e o grafo colapsa (o "1 grafo único" da Fase 1 do RIC).

Leitura robusta (docs/02 A2 / docs/05): as 3 linhas de pixels de um patch são idênticas no
glifo limpo, logo a variância ENTRE elas estima o ruído do ambiente. Com isso dá para (i)
corrigir a atenuação da correlação e (ii) ponderar cada aresta pela fração de variância que é
sinal — o par não confiável pesa 0 e é ignorado, em vez de virar bit aleatório.
"""
import itertools
import numpy as np
from scipy.linalg import hadamard
from ricemotions.mundo import NV, T, CLASSES, FAMILIAS

R = 3
NROWS = 16                               # linhas-de-patch do formato base
SL_NIVEL, SL_POL, SL_CORPO, SL_CARGA = slice(0, 2), slice(2, 4), slice(4, 10), slice(10, 16)
SL_RES = slice(16, 22)                   # banda opcional de resíduo (6 canais)
WALSH = hadamard(32).astype(float)[1:]            # 31 portadoras ortogonais de média zero
IU = np.triu_indices(NV, 1)
NP = len(IU[0])                                    # 15 pares


# ---------------- partições (alfabeto da carga) ----------------
def set_partitions(n=NV):
    def rec(i, labels, k):
        if i == n:
            yield tuple(labels); return
        for b in range(k + 1):
            yield from rec(i + 1, labels + [b], max(k, b + 1))
    yield from rec(0, [], 0)


def comembership(labels):
    l = np.array(labels)
    return (l[IU[0]] == l[IU[1]]).astype(np.int8)


ALL_PARTS = list(set_partitions())
ALL_BITS = np.array([comembership(p) for p in ALL_PARTS])      # (203, 15)


def codebook(d_min, seed=0):
    """Seleção gulosa (como no RIC): mantém partições com d_I >= d_min entre si."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(ALL_PARTS))
    chosen = []
    for i in order:
        if all(np.abs(ALL_BITS[i] - ALL_BITS[j]).sum() >= d_min for j in chosen):
            chosen.append(i)
    chosen = sorted(chosen)
    return [ALL_PARTS[i] for i in chosen], ALL_BITS[chosen]


# ---------------- isomorfismo da carga (próximo passo; ver docs/04) ----------------
def shape(labels):
    """Tipo de isomorfismo: tamanhos dos blocos em ordem decrescente.

    Duas partições viram o MESMO grafo após permutar vértices <=> mesmo shape.
    Nº de shapes de 6 vértices = nº de partições de 6 = 11, logo o teto da carga
    sob permutação livre é log2(11) = 3,46 bits."""
    l = np.array(labels)
    return tuple(sorted((int(np.sum(l == b)) for b in np.unique(l)), reverse=True))


def shape_representatives():
    """Índice da primeira partição de cada shape (uma palavra por isomorfismo)."""
    seen, out = set(), []
    for i, p in enumerate(ALL_PARTS):
        s = shape(p)
        if s not in seen:
            seen.add(s); out.append(i)
    return out


def codebook_up_to_isomorphism(d_min, seed=0):
    """Codebook com NO MÁXIMO uma palavra por classe de isomorfismo.

    Por que existe: `decode_payload(..., perms=ALL_PERMS)` minimiza sobre (p, q).
    Se duas palavras do codebook são isomorfas, ambas atingem distância 0 para o
    mesmo glifo e o desempate é arbitrário — medido: 0,27 em vez de ~1,0.
    """
    cand = shape_representatives()
    rng = np.random.default_rng(seed)
    chosen = []
    for i in rng.permutation(cand):
        if all(np.abs(ALL_BITS[i] - ALL_BITS[j]).sum() >= d_min for j in chosen):
            chosen.append(int(i))
    chosen = sorted(chosen)
    return [ALL_PARTS[i] for i in chosen], ALL_BITS[chosen]


# ---------------- renderização ----------------
def render(X, v, act, fam, payload_labels, rng, residuo=None):
    """residuo: (6, T) opcional em [0,1] -> acrescenta a banda RESÍDUO (linhas 16-21)."""
    nrows = NROWS + (6 if residuo is not None else 0)
    rows = np.zeros((nrows, T))
    rows[0] = np.clip(0.5 + 0.4 * np.tanh(3 * v), 0, 1)
    rows[1] = np.clip(act, 0, 1)
    nb = max(payload_labels) + 1
    idx = rng.choice(len(WALSH), 1 + nb, replace=False)
    c = WALSH[idx[0]]
    s = 1.0 if fam == "alegria" else -1.0
    rows[2] = 0.5 + 0.25 * c
    rows[3] = 0.5 + 0.25 * s * c
    rows[SL_CORPO] = X
    sg = rng.choice([-1.0, 1.0], nb)
    for i, b in enumerate(payload_labels):
        rows[10 + i] = 0.5 + 0.25 * sg[b] * WALSH[idx[1 + b]]
    if residuo is not None:
        rows[SL_RES] = np.clip(residuo, 0, 1)
    img = np.repeat(rows, R, axis=0)
    return np.round(np.clip(img, 0, 1) * 255) / 255.0


# ---------------- transformações da imagem ----------------
def t_noise(img, s, rng): return img + rng.normal(0, s, img.shape)
def t_bright(img, g, o): return img * g + o
def t_blur(img):
    k = np.array([1, 1, 1]) / 3.0
    return np.stack([np.convolve(np.pad(r, 1, mode="edge"), k, mode="valid") for r in img])
def t_miscal(img, rng):
    b = img.reshape(-1, R, T)
    g = rng.uniform(0.6, 1.4, (b.shape[0], 1, 1)); o = rng.uniform(-0.15, 0.15, (b.shape[0], 1, 1))
    return (b * g + o).reshape(-1, T)
def t_perm(img, rng, keep=()):
    """Permuta as linhas-de-patch do CORPO e da CARGA (a 'rotação' do RIC: permuta vértices).
    keep: índices do corpo que ficam fixos (âncoras). A carga é sempre permutada por inteiro.
    A banda RESÍDUO (se existir) não é permutada: ela carrega o índice da simetria."""
    b = img.reshape(-1, R, T).copy()
    free = [i for i in range(NV) if i not in keep]
    perm_corpo = np.arange(NV)
    perm_corpo[free] = np.array(free)[rng.permutation(len(free))]
    b[4:10] = b[4:10][perm_corpo]
    b[10:16] = b[10:16][rng.permutation(NV)]
    return b.reshape(-1, T)


def apply_perm(img, p):
    """Aplica a permutação p (len 6) às linhas do CORPO — o resíduo escrito como simetria."""
    b = img.reshape(-1, R, T).copy()
    b[SL_CORPO] = b[SL_CORPO][np.asarray(p)]
    return b.reshape(-1, T)


def undo_perm(img, p):
    """Desfaz `apply_perm` (inversa da permutação)."""
    inv = np.argsort(np.asarray(p))
    return apply_perm(img, inv)


# ---------------- leitura RIC ----------------
def patches(img): return img.reshape(-1, R, T).mean(1)


def corr(M):
    Z = M - M.mean(1, keepdims=True)
    Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9)
    return Z @ Z.T


def body_graph(img, tau):
    c = corr(patches(img)[SL_CORPO])[IU]
    return np.concatenate([c > tau, c < -tau]).astype(np.int8)       # 30 bits (camada + e camada -)


def payload_graph(img, tau=0.5):
    c = corr(patches(img)[SL_CARGA])[IU]
    return (np.abs(c) > tau).astype(np.int8)                          # 15 bits


# ---------------- leitura robusta (resíduo estimado na própria redundância) ----------------
def sigma2_pixels(img):
    """σ² do ruído de PIXEL, estimado pela redundância R=3 do glifo.

    As 3 linhas de pixels de um patch são idênticas quando o glifo é escrito; portanto a
    variância entre elas é 100% ruído do ambiente. É o "termômetro" gratuito do canal —
    sem nenhuma informação do rótulo.
    """
    b = img.reshape(-1, R, T)
    return float(np.var(b, axis=1, ddof=1).mean())


def body_cont(img, corrigir=True):
    """Arestas CONTÍNUAS (grafo ponderado) do corpo: `(c, w)`.

    c (15,)  cosseno centralizado por par, corrigido pela atenuação do ruído:
             c_true ≈ c_obs · sqrt(vo_i·vo_j / (s_i·s_j)), com s² = vo² − σ²̂/R.
    w (15,)  confiabilidade da aresta = fração da variância temporal que é SINAL.
             Areasta não confiável (s² ≤ 0) pesa 0 e é IGNORADA na decodificação,
             em vez de virar um bit aleatório — é isso que derruba o Hamming duro.

    `corrigir=False` devolve (c, 1) puro, para ablação.
    """
    P = patches(img)[SL_CORPO]
    c = corr(P)[IU]
    if not corrigir:
        return c, np.ones(NP)
    n = sigma2_pixels(img) / R                       # ruído na MÉDIA do patch
    vo = P.var(1)                                    # variância observada (sinal + ruído)
    si = np.maximum(vo - n, 0.0)                     # variância do sinal estimada
    si_s = np.maximum(si, 1e-6 * np.maximum(vo, 1e-12))
    att = np.sqrt(np.clip(vo[IU[0]] * vo[IU[1]] / (si_s[IU[0]] * si_s[IU[1]]), 1.0, 1e4))
    w = (si / np.maximum(vo, 1e-12))[IU[0]] * (si / np.maximum(vo, 1e-12))[IU[1]]
    return np.clip(c * att, -1.0, 1.0), w


def body_prototypes(imgs, y, n_cls=6, corrigir=True):
    """Protótipo contínuo por classe: média das arestas do CORPO (imagens de treino)."""
    C = np.array([body_cont(i, corrigir)[0] for i in imgs])
    return np.stack([C[y == k].mean(0) for k in range(n_cls)])


def decode_body_cont(C, W, protos):
    """Menor distância PONDERADA pela confiabilidade de cada aresta.

    C (n,15) arestas observadas · W (n,15) pesos · protos (k,15) · -> (n,) rótulos.
    """
    if W is None:
        W = np.ones_like(C)
    w = np.where(W.sum(-1, keepdims=True) < 1e-9, 1.0, W)      # fallback: sem info, não enviesa
    d = (w[:, None, :] * (C[:, None, :] - protos[None, :, :]) ** 2).sum(-1)
    return np.argmin(d / w.sum(-1)[:, None], axis=1)


def read_family_relational(img):
    c = corr(patches(img)[SL_POL])[0, 1]
    return 0 if c > 0 else 1                                          # 0 alegria, 1 tristeza


def read_family_level(img):
    return 0 if patches(img)[0].mean() > 0.5 else 1


def decode_payload(img, bits, parts, perms=None):
    g = payload_graph(img)
    if perms is None:
        return int(np.argmin(np.abs(bits - g).sum(1)))
    best, arg = 1e9, 0
    for p in perms:
        pb = np.array([comembership(np.array(q)[p]) for q in parts])
        d = np.abs(pb - g).sum(1); i = int(np.argmin(d))
        if d[i] < best: best, arg = d[i], i
    return arg


# ---------------- permutações de vértices (isomorfismo / âncoras) ----------------
def perm_bits_index(p):
    pos = {pair: n for n, pair in enumerate(zip(*IU))}
    return np.array([pos[tuple(sorted((p[i], p[j])))] for i, j in zip(*IU)])


ALL_PERMS = [np.array(p) for p in itertools.permutations(range(NV))]
ANCHOR_PERMS = [np.array([0, 1] + list(p)) for p in itertools.permutations(range(2, NV))]   # E,T fixas


def decode_body_alphabet(G, R_, lab, perms=None):
    """G: (n, 30); R_: (m, 30) alfabeto; lab: (m,). perms: lista de permutações de vértices."""
    if perms is None:
        return np.array([lab[np.argmin(np.abs(R_ - g).sum(1))] for g in G])
    idxs = [perm_bits_index(p) for p in perms]
    RP = np.stack([np.concatenate([R_[:, ix], R_[:, NP + ix]], 1) for ix in idxs])   # (n_perm, m, 30)
    out = []
    for g in G:
        d = np.abs(RP - g).sum(-1).min(0)
        out.append(lab[int(np.argmin(d))])
    return np.array(out)


def alphabet(G, y):
    from collections import Counter, defaultdict
    cnt = defaultdict(Counter)
    for g, l in zip(map(tuple, G), y): cnt[g][int(l)] += 1
    A = np.array([list(g) for g in cnt], dtype=np.int8)
    lab = np.array([cnt[g].most_common(1)[0][0] for g in cnt])
    return A, lab


# ---------------- resíduo como SIMETRIA (roteamento C de docs/05) ----------------
def canon_order(B):
    """Ordem canônica de um conjunto de linhas-de-patch: pela média da linha, com
    desempate lexicográfico (invariante à permutação — por isso escritor e leitor
    concordam sem se comunicarem).

    Aceita tanto a matriz de patches (n, T) quanto o bloco de pixels (n, R, T);
    no segundo caso a chave é calculada sobre a média das R linhas redundantes.
    """
    P = B.mean(1) if B.ndim == 3 else B             # (n, T) em ambos os casos
    keys = np.vstack([P[:, ::-1].T, P.mean(1)])     # última chave = primária
    return np.lexsort(keys)


def canon_img(img):
    """Devolve o glifo com o CORPO em ordem canônica (a escrita da simetria)."""
    b = img.reshape(-1, R, T).copy()
    b[SL_CORPO] = b[SL_CORPO][canon_order(b[SL_CORPO])]
    return b.reshape(-1, T)


def escrever_simetria(img, p):
    """CORPO = canônico[p]: a forma canônica é embaralhada pela permutação do resíduo.
    Zero linhas extras — a informação viaja na simetria dos vértices."""
    b = img.reshape(-1, R, T).copy()
    b[SL_CORPO] = b[SL_CORPO][canon_order(b[SL_CORPO])]
    b[SL_CORPO] = b[SL_CORPO][np.asarray(p, dtype=int)]
    return b.reshape(-1, T)


def simetria_ordem(img):
    """Recupera `p` a partir do glifo, sem protótipos nem rótulo.

    Prova: observado = K[p] com K ordenado pela chave; o leitor reordena o observado
    pela MESMA chave, logo `ordem_leitor = p⁻¹` e `p = argsort(ordem_leitor)`.
    """
    return np.argsort(canon_order(patches(img)[SL_CORPO]))


def ler_corpo_canonico(img):
    """CORPO do glifo já alinhado na forma canônica (é o que se compara ao alfabeto)."""
    b = img.reshape(-1, R, T)
    out = b.copy()
    out[SL_CORPO] = b[SL_CORPO][canon_order(b[SL_CORPO])]
    return out.reshape(-1, T)


# ---------------- linhas de base por NÍVEL (mesma imagem) ----------------
def level_feats(img, kind):
    P = patches(img)[SL_CORPO]
    mean = P.mean(1)
    delta = P[:, -8:].mean(1) - P[:, :8].mean(1)
    return {"nivel": mean, "delta": delta, "nivel+delta": np.concatenate([mean, delta])}[kind]


class LDA:
    def fit(self, F, y, ridge=1e-3):
        self.cls = np.unique(y)
        self.mu = np.stack([F[y == k].mean(0) for k in self.cls])
        Sw = sum(np.cov(F[y == k].T) * (np.sum(y == k) - 1) for k in self.cls) / (len(y) - len(self.cls))
        self.P = np.linalg.inv(Sw + ridge * np.eye(F.shape[1]))
        return self
    def predict(self, F):
        S = F @ self.P @ self.mu.T - 0.5 * np.einsum("kd,de,ke->k", self.mu, self.P, self.mu)
        return self.cls[np.argmax(S, 1)]


def balanced_acc(pred, y):
    return float(np.mean([np.mean(pred[y == k] == k) for k in np.unique(y)]))


# ---------------- mensagem em vários glifos ----------------
def text_to_digits(msg, base):
    n = int.from_bytes(msg.encode("utf-8"), "big")
    d = []
    while n: d.append(n % base); n //= base
    return d[::-1] or [0]


def digits_to_text(d, base):
    n = 0
    for x in d: n = n * base + int(x)
    return n.to_bytes((n.bit_length() + 7) // 8, "big").decode("utf-8", errors="replace")
