"""Testes da estrutura de saida de uma run. Puros: nao abrem browser."""
import pytest

from pipeline.render import caminho_arte, prepara_saida


def slides(*formatos):
    return [{"formato": f, "tipo": "capa"} for f in formatos]


def pngs(base):
    return sorted(p.relative_to(base).as_posix() for p in base.rglob("*.png"))


def test_arte_vai_para_a_subpasta_do_formato():
    assert caminho_arte(1, {"formato": "feed"}) == "artes/feed/slide-01-feed.png"
    assert caminho_arte(2, {"formato": "story"}) == "artes/story/slide-02-story.png"


def test_indice_recebe_dois_digitos():
    assert caminho_arte(7, {"formato": "feed"}).endswith("slide-07-feed.png")
    assert caminho_arte(10, {"formato": "feed"}).endswith("slide-10-feed.png")


def test_formato_ausente_assume_feed():
    assert caminho_arte(1, {}) == "artes/feed/slide-01-feed.png"


def test_cria_uma_subpasta_por_formato_da_run(tmp_path):
    prepara_saida(tmp_path, slides("feed", "story", "feed"))
    assert (tmp_path / "artes" / "feed").is_dir()
    assert (tmp_path / "artes" / "story").is_dir()


def test_nao_cria_subpasta_de_formato_ausente(tmp_path):
    prepara_saida(tmp_path, slides("feed", "feed"))
    assert not (tmp_path / "artes" / "story").exists()


def test_run_que_encolhe_nao_deixa_arte_obsoleta(tmp_path):
    # antes da correcao, os PNGs 04..08 da run anterior sobreviviam:
    # o relatorio dizia 3 slides e a pasta tinha 8
    grande = slides(*(["feed"] * 8))
    prepara_saida(tmp_path, grande)
    for i, s in enumerate(grande):
        (tmp_path / caminho_arte(i + 1, s)).write_bytes(b"antigo")
    assert len(pngs(tmp_path)) == 8

    pequena = slides("feed", "feed", "feed")
    prepara_saida(tmp_path, pequena)
    assert pngs(tmp_path) == ["artes/feed/slide-01-feed.png",
                              "artes/feed/slide-02-feed.png",
                              "artes/feed/slide-03-feed.png"]


def test_formato_abandonado_tem_a_subpasta_removida(tmp_path):
    antes = slides("feed", "story")
    prepara_saida(tmp_path, antes)
    for i, s in enumerate(antes):
        (tmp_path / caminho_arte(i + 1, s)).write_bytes(b"antigo")

    prepara_saida(tmp_path, slides("feed"))
    assert not (tmp_path / "artes" / "story").exists()


def test_subpasta_da_run_atual_sobrevive_mesmo_vazia(tmp_path):
    # as pastas nascem vazias e so recebem os PNGs no screenshot;
    # a limpeza nao pode apaga-las nesse intervalo
    prepara_saida(tmp_path, slides("feed", "story"))
    assert (tmp_path / "artes" / "feed").is_dir()
    assert (tmp_path / "artes" / "story").is_dir()


def test_preparar_e_idempotente(tmp_path):
    s = slides("feed", "story")
    prepara_saida(tmp_path, s)
    for i, sl in enumerate(s):
        (tmp_path / caminho_arte(i + 1, sl)).write_bytes(b"arte")
    prepara_saida(tmp_path, s)
    assert len(pngs(tmp_path)) == 2
