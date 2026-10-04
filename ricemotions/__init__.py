"""
ricemotions — emoção escrita em pixels (ponte entre o projeto PIXEL/RIC e o TEOA).

Três camadas, três responsabilidades:

``ricemotions.mundo``
    O **mundo**: gera episódios de 32 passos em seis canais internos (E,T,C,B,G,N)
    e os rotula por (família afetiva) x (procedência). É aqui que mora o TEOA
    (valência = nível + taxa da distância ao alvo).

``ricemotions.glifo``
    O **glifo**: transforma um episódio em imagem 48x32 e a lê de volta pelo RIC
    (incidência relacional: correlação entre linhas -> grafo -> decodificação por
    menor distância). É aqui que mora o lado PIXEL.

``ricemotions.experimentos``
    Os **experimentos** E1-E4 e as figuras. Só aqui existe I/O de disco.

Uso::

    python run_all.py            # testes + experimentos + figuras
    python -m ricemotions.experimentos
    python tests/test_smoke.py
"""

__version__ = "0.1.0"
__all__ = ["mundo", "glifo", "experimentos"]
