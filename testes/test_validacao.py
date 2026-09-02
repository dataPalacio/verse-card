"""Testes do schema e das mensagens de erro em pt-BR."""
import copy
import json
from pathlib import Path

import pytest

from pipeline.validacao import ErroDeConteudo, valida_arquivo, valida_conteudo

RAIZ = Path(__file__).resolve().parent.parent
REAL = RAIZ / "conteudo" / "proverbios-19-21.json"
EXEMPLO = RAIZ / "conteudo" / "exemplos" / "exemplo-minimo.json"


@pytest.fixture
def base():
    return json.loads(REAL.read_text(encoding="utf-8"))


@pytest.mark.parametrize("caminho", [REAL, EXEMPLO])
def test_conteudo_real_do_projeto_e_valido(caminho):
    # calibracao: o schema existe para descrever o conteudo que ja funciona
    assert valida_arquivo(caminho)["slides"]


def test_linhas_vazia_vira_erro_de_validacao(base):
    # antes da reestruturacao isso estourava IndexError no meio do render
    base["slides"][0]["versiculos"][0]["linhas"] = []
    with pytest.raises(ErroDeConteudo) as exc:
        valida_conteudo(base)
    assert "slides[0].versiculos[0].linhas" in str(exc.value)


def test_capa_sem_livro_reprova(base):
    del base["slides"][0]["livro"]
    with pytest.raises(ErroDeConteudo) as exc:
        valida_conteudo(base)
    assert "livro" in str(exc.value) and "slides[0]" in str(exc.value)


def test_interno_sem_paragrafos_reprova(base):
    del base["slides"][2]["paragrafos"]
    with pytest.raises(ErroDeConteudo) as exc:
        valida_conteudo(base)
    assert "paragrafos" in str(exc.value)


def test_foto_sem_alt_reprova(base):
    # acessibilidade: o CHANGELOG do V5 lista o alt como conquista
    del base["slides"][0]["foto_alt"]
    with pytest.raises(ErroDeConteudo) as exc:
        valida_conteudo(base)
    assert "foto_alt" in str(exc.value)


def test_tipo_invalido_reprova(base):
    base["slides"][0]["tipo"] = "capinha"
    with pytest.raises(ErroDeConteudo):
        valida_conteudo(base)


def test_run_id_fora_do_padrao_reprova(base):
    base["run_id"] = "solto"
    with pytest.raises(ErroDeConteudo) as exc:
        valida_conteudo(base)
    assert "run_id" in str(exc.value)


def test_run_id_com_barra_reprova(base):
    # protege a derivacao da pasta de saida contra path traversal
    base["run_id"] = "2026-09-01-../../escapou"
    with pytest.raises(ErroDeConteudo):
        valida_conteudo(base)


def test_sem_slides_reprova(base):
    base["slides"] = []
    with pytest.raises(ErroDeConteudo):
        valida_conteudo(base)


def test_dois_erros_sao_reportados_juntos(base):
    del base["slides"][3]["titulo"]
    del base["slides"][5]["paragrafos"]
    with pytest.raises(ErroDeConteudo) as exc:
        valida_conteudo(base)
    assert len(exc.value.problemas) == 2


def test_mensagem_sai_em_portugues(base):
    del base["slides"][2]["titulo"]
    with pytest.raises(ErroDeConteudo) as exc:
        valida_conteudo(base)
    assert "exige o campo" in str(exc.value)
