#!/usr/bin/env python3
"""
Construtores de HTML do Verse Card V5.

Funcoes puras: recebem um dicionario de slide e devolvem string HTML.
Nenhuma delas toca disco nem depende de browser — sao o alvo dos testes
unitarios em sistema/testes/test_construtores.py.
"""
import html as H

LIMITE_LIVRO_LONGO = 9  # acima disso, o corpo do nome do livro reduz (regra tipografica)


def esc(t: str) -> str:
    # quote=False e intencional: as aspas curvas do texto biblico passam intactas
    return H.escape(str(t), quote=False)


def bloco_referencia(s):
    livro = esc(s["livro"])
    longo = " longo" if len(s["livro"]) > LIMITE_LIVRO_LONGO else ""
    ref = esc(s.get("referencia", ""))
    linha_ref = f'<p class="ref-verse">{ref}</p>' if ref else ""
    return f'<header class="ref"><h1 class="ref-book{longo}">{livro}</h1>{linha_ref}</header>'


def bloco_foto(s):
    if not s.get("foto"):
        return '<figure class="photo"></figure>'
    alt = esc(s.get("foto_alt", ""))
    h = 900 if s.get("formato") == "story" else 700
    return (f'<figure class="photo"><img src="{esc(s["foto"])}" width="1400" height="{h}" '
            f'fetchpriority="high" alt="{alt}"></figure>')


def bloco_passagem(s):
    out = []
    for v in s.get("versiculos", []):
        linhas = v["linhas"]
        corpo = f'<span class="n">{esc(v["n"])}</span>{esc(linhas[0])}'
        corpo += "".join(f'<span class="cont">{esc(l)}</span>' for l in linhas[1:])
        out.append(f"<p>{corpo}</p>")
    return f'<div class="passage">{"".join(out)}</div>'


def bloco_paragrafos(s):
    ps = "".join(f"<p>{esc(p)}</p>" for p in s.get("paragrafos", []))
    return f'<div class="passage passage-interno">{ps}</div>'


def rodape(s, handle):
    return (f'<footer class="foot"><span class="brand" translate="no">{esc(handle)}</span>'
            f'<span class="right"><span>{esc(s.get("hint", "arraste"))}</span>'
            f'<span class="selo" role="img" aria-label="Sua Palavra Diária"></span></span></footer>')


def render_slide(s, handle):
    fmt = s.get("formato", "feed")
    agua = ('<span class="agua-wrap" aria-hidden="true"><span class="selo-agua"></span></span>'
            if s.get("marca_dagua") else "")
    if s["tipo"] == "capa":
        miolo = bloco_referencia(s) + bloco_foto(s) + bloco_passagem(s)
    else:
        cabeca = f'<header class="ref"><h2 class="ref-book longo">{esc(s["titulo"])}</h2></header>'
        miolo = cabeca + (bloco_foto(s) if s.get("foto") else "") + bloco_paragrafos(s)
    return (f'<div class="slide {fmt}"><article class="card">'
            f'{agua}{miolo}{rodape(s, handle)}</article></div>')
