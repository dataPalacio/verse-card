"""Trava o anti-drift: o template autocontido tem que refletir o CSS canonico."""
import re

from sistema.pipeline.sincroniza_template import (HTML, base64_esperado, conferir,
                                          css_resolvido, html_esperado)


def test_artefatos_gerados_estao_em_sincronia():
    # Este teste falhava antes da reestruturacao: faltavam as regras
    # .passage-interno no template autocontido.
    assert conferir() == []


def test_bloco_style_equivale_ao_css_canonico():
    inline = re.search(r"(?s)<style>(.*?)</style>", HTML.read_text(encoding="utf-8")).group(1)
    assert inline.strip() == css_resolvido().strip()


def test_template_contem_as_regras_do_slide_interno():
    css = HTML.read_text(encoding="utf-8")
    assert ".passage-interno" in css
    assert ".story .passage-interno" in css


def test_placeholder_do_logo_foi_substituido():
    assert "__LOGO_B64__" not in HTML.read_text(encoding="utf-8")


def test_base64_corresponde_ao_png_da_marca():
    from sistema.pipeline.sincroniza_template import LOGO_B64
    assert LOGO_B64.read_text().strip() == base64_esperado()


def test_corpo_de_demonstracao_e_preservado():
    # o <body> nao e derivavel do CSS; a sincronizacao nao pode apaga-lo
    html = html_esperado()
    assert html.count('class="slide ') >= 4


def test_arquivo_gerado_avisa_que_nao_deve_ser_editado():
    assert HTML.read_text(encoding="utf-8").lstrip().startswith("<!-- GERADO")
