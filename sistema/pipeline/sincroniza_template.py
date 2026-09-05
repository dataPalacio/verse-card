#!/usr/bin/env python3
"""
Sincroniza os artefatos derivados a partir das fontes canonicas.

  visual/modelo/carrossel.html  <- visual/modelo/carrossel.css + visual/marca/logo-base64.txt
  visual/marca/logo-base64.txt  <- visual/marca/logo.png

O template autocontido e GERADO: so o interior de <style>...</style> e
reescrito. A casca HTML (head e os slides de demonstracao no <body>) e
preservada intacta, porque nao e derivavel do CSS.

Uso:
    python -m sistema.pipeline.sincroniza_template            # grava
    python -m sistema.pipeline.sincroniza_template --conferir # so verifica, sai 1 se divergir
"""
import base64
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
CSS = RAIZ / "visual" / "modelo" / "carrossel.css"
HTML = RAIZ / "visual" / "modelo" / "carrossel.html"
LOGO_PNG = RAIZ / "visual" / "marca" / "logo.png"
LOGO_B64 = RAIZ / "visual" / "marca" / "logo-base64.txt"

AVISO = ("<!-- GERADO por sistema/pipeline/sincroniza_template.py a partir de visual/modelo/carrossel.css.\n"
         "     NAO EDITAR A MAO. Rode: .\\executar.ps1 -Acao sincronizar -->\n")


def css_resolvido() -> str:
    """CSS canonico com o placeholder do logo substituido pelo base64 real."""
    return CSS.read_text(encoding="utf-8").replace("__LOGO_B64__", LOGO_B64.read_text().strip())


def base64_esperado() -> str:
    return base64.b64encode(LOGO_PNG.read_bytes()).decode("ascii")


def html_esperado() -> str:
    """Casca atual do HTML com o bloco <style> trocado pelo CSS canonico."""
    atual = HTML.read_text(encoding="utf-8")
    novo = re.sub(r"(?s)(<style>).*?(</style>)",
                  lambda m: m.group(1) + "\n" + css_resolvido() + m.group(2),
                  atual, count=1)
    novo = re.sub(r"\A<!-- GERADO.*?-->\s*", "", novo, count=1, flags=re.S)
    novo = AVISO + novo
    return novo


def conferir() -> list:
    """Devolve lista de divergencias encontradas (vazia = tudo sincronizado)."""
    problemas = []
    if LOGO_B64.read_text().strip() != base64_esperado():
        problemas.append("visual/marca/logo-base64.txt divergiu de visual/marca/logo.png")
    if HTML.read_text(encoding="utf-8") != html_esperado():
        problemas.append("visual/modelo/carrossel.html divergiu de visual/modelo/carrossel.css")
    return problemas


def sincronizar():
    LOGO_B64.write_text(base64_esperado(), encoding="utf-8")
    HTML.write_text(html_esperado(), encoding="utf-8")


def main():
    if "--conferir" in sys.argv:
        problemas = conferir()
        if problemas:
            print("Artefatos gerados fora de sincronia:")
            for p in problemas:
                print(f"  - {p}")
            print("\nRode: .\\executar.ps1 -Acao sincronizar")
            sys.exit(1)
        print("Artefatos gerados em sincronia com as fontes canonicas.")
        return
    sincronizar()
    print(f"sincronizado: {HTML.relative_to(RAIZ)}")
    print(f"sincronizado: {LOGO_B64.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
