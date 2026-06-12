import sys
import argparse
import contextlib
from carregar_jocs import TestRunner


class Tee:
    """Escriu simultàniament a múltiples streams (e.g. stdout + fitxer)."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for s in self.streams:
            s.write(text)

    def flush(self):
        for s in self.streams:
            s.flush()


parser = argparse.ArgumentParser(description="Executa proves de gramàtiques amb CKY.")
parser.add_argument("fitxer", help="Fitxer de problemes (.txt)")
parser.add_argument("--tolerancia", type=float, default=1e-6, help="Tolerància per a problemes probabilístics (default: 1e-6)")
parser.add_argument("--output", metavar="FITXER", help="Desa els resultats en un fitxer de text")
args = parser.parse_args()

runner = TestRunner()
runner.carregar(args.fitxer)

if args.output:
    with open(args.output, "w", encoding="utf-8") as f_out:
        with contextlib.redirect_stdout(Tee(sys.stdout, f_out)):
            runner.executar(tolerancia=args.tolerancia)
else:
    runner.executar(tolerancia=args.tolerancia)