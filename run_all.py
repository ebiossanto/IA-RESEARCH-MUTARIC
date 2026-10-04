"""Ponto de entrada único do ricemotions.

    python run_all.py                # testes + experimentos (E1-E10, E10b) + figuras
    python run_all.py --so-testes    # só a sanidade (segundos)
    python run_all.py --so-experimentos

Os experimentos levam alguns minutos e reescrevem figs/*.png e
resultados/resultados.json.
"""
import argparse
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    print("\n$ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=RAIZ, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--so-testes", action="store_true", help="roda só tests/test_smoke.py")
    p.add_argument("--so-experimentos", action="store_true", help="roda só ricemotions.experimentos")
    a = p.parse_args()

    if not a.so_experimentos:
        run([sys.executable, os.path.join("tests", "test_smoke.py")])
    if not a.so_testes:
        run([sys.executable, "-m", "ricemotions.experimentos"])
    print("\nOK.")


if __name__ == "__main__":
    main()
