#!/usr/bin/env python3
r"""
Valida um content.json sem renderizar nada.

Uso:
    python -m sistema.pipeline.validar conteudos/publicados/001-confiar-na-espera/conteudo.json

Sai 0 se aprovado, 2 se o conteudo for invalido.
"""
import sys
from pathlib import Path

from sistema.pipeline.validacao import ErroDeConteudo, valida_arquivo


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    caminho = Path(sys.argv[1])
    try:
        conteudo = valida_arquivo(caminho)
    except ErroDeConteudo as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
    print(f"conteudo valido: {caminho} "
          f"(run_id={conteudo['run_id']}, {len(conteudo['slides'])} slides)")
    print(f"publicacao prevista: {caminho.parent / 'publicacao'}")


if __name__ == "__main__":
    main()
