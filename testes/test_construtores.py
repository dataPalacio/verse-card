"""Testes das funcoes puras de construcao de HTML. Nao exigem browser."""
import pytest

from pipeline.construtores import (LIMITE_LIVRO_LONGO, bloco_foto, bloco_passagem,
                                   bloco_referencia, esc, render_slide)

HANDLE = "@sua.palavra.diaria"


def test_esc_escapa_e_comercial_e_sinais_de_menor():
    assert esc("Ele & <ela>") == "Ele &amp; &lt;ela&gt;"


def test_esc_preserva_aspas_curvas():
    # quote=False e intencional: as aspas tipograficas do texto biblico
    # precisam chegar intactas ao HTML.
    texto = '\u201cEsquecam as coisas\u201d'
    assert esc(texto) == texto


def test_livro_curto_nao_recebe_classe_longo():
    html = bloco_referencia({"livro": "Isaias", "referencia": "43:18"})
    assert 'class="ref-book"' in html
    assert "longo" not in html


def test_livro_longo_recebe_classe_longo():
    html = bloco_referencia({"livro": "Proverbios", "referencia": "19:21"})
    assert 'class="ref-book longo"' in html


@pytest.mark.parametrize("tamanho,espera_longo", [(9, False), (10, True)])
def test_limiar_exato_do_nome_longo(tamanho, espera_longo):
    # a regra e len > 9; 9 caracteres ainda e curto, 10 ja e longo
    assert LIMITE_LIVRO_LONGO == 9
    html = bloco_referencia({"livro": "A" * tamanho})
    assert ("longo" in html) is espera_longo


def test_referencia_ausente_nao_emite_paragrafo_vazio():
    html = bloco_referencia({"livro": "Isaias"})
    assert "ref-verse" not in html


def test_foto_ausente_gera_figure_vazia():
    assert bloco_foto({}) == '<figure class="photo"></figure>'
    assert "<img" not in bloco_foto({})


def test_altura_da_foto_por_formato():
    feed = bloco_foto({"foto": "http://x/y.jpg", "foto_alt": "a", "formato": "feed"})
    story = bloco_foto({"foto": "http://x/y.jpg", "foto_alt": "a", "formato": "story"})
    assert 'height="700"' in feed
    assert 'height="900"' in story


def test_primeira_linha_cola_no_numero_e_demais_viram_cont():
    html = bloco_passagem({"versiculos": [{"n": "21", "linhas": ["primeira", "segunda", "terceira"]}]})
    assert '<span class="n">21</span>primeira' in html
    assert html.count('<span class="cont">') == 2


def test_slide_emite_exatamente_um_selo():
    # trava a Regra 1 de regras/brand-mark-rules.md em nivel unitario,
    # sem precisar renderizar no Chromium
    slide = {"tipo": "interno", "formato": "feed", "titulo": "T", "paragrafos": ["p"]}
    assert render_slide(slide, HANDLE).count('class="selo"') == 1


def test_marca_dagua_nao_duplica_o_selo():
    slide = {"tipo": "interno", "formato": "feed", "titulo": "T",
             "paragrafos": ["p"], "marca_dagua": True}
    html = render_slide(slide, HANDLE)
    assert html.count("agua-wrap") == 1
    assert html.count('class="selo-agua"') == 1
    assert html.count('class="selo"') == 1


def test_slide_sem_marca_dagua_nao_tem_agua_wrap():
    slide = {"tipo": "interno", "formato": "feed", "titulo": "T", "paragrafos": ["p"]}
    assert "agua-wrap" not in render_slide(slide, HANDLE)


def test_handle_marcado_como_nao_traduzivel():
    slide = {"tipo": "interno", "formato": "feed", "titulo": "T", "paragrafos": ["p"]}
    assert 'translate="no"' in render_slide(slide, HANDLE)
