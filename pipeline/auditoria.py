#!/usr/bin/env python3
"""
Auditoria de qualidade de render.

avalia_slide() e pura: recebe as medidas coletadas no browser e devolve o
status. Separada do render para poder ser testada sem Chromium.
Regras em regras/render-quality-checklist.md.
"""


def avalia_slide(medida: dict) -> str:
    """medida: {"overflowY": int, "overflowX": int, "selos": int} -> "OK" | "FALHA ..."

    Overflow tem precedencia sobre contagem de selo: um cartao que estoura
    invalida a arte independentemente da marca.
    """
    if medida["overflowY"] or medida["overflowX"]:
        return f"FALHA overflow y={medida['overflowY']} x={medida['overflowX']}"
    if medida["selos"] != 1:
        return f"FALHA selo ocorrencias={medida['selos']}"
    return "OK"


def resumo(status_por_slide):
    """Conta aprovacoes e reprovacoes de uma run."""
    ok = sum(1 for s in status_por_slide if s == "OK")
    return {"slides": len(status_por_slide), "ok": ok, "falhas": len(status_por_slide) - ok}
