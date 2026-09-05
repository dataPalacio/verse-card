"""Testes da auditoria de qualidade. Puros: nao abrem browser."""
from sistema.pipeline.auditoria import avalia_slide, resumo


def test_slide_limpo_aprova():
    assert avalia_slide({"overflowY": 0, "overflowX": 0, "selos": 1}) == "OK"


def test_overflow_vertical_reprova_citando_a_medida():
    # 94px foi o estouro real do V4 registrado no CHANGELOG
    status = avalia_slide({"overflowY": 94, "overflowX": 0, "selos": 1})
    assert status.startswith("FALHA")
    assert "94" in status


def test_overflow_horizontal_reprova():
    assert avalia_slide({"overflowY": 0, "overflowX": 12, "selos": 1}).startswith("FALHA")


def test_selo_duplicado_reprova():
    status = avalia_slide({"overflowY": 0, "overflowX": 0, "selos": 2})
    assert "selo" in status and "2" in status


def test_selo_ausente_reprova():
    assert avalia_slide({"overflowY": 0, "overflowX": 0, "selos": 0}).startswith("FALHA")


def test_overflow_tem_precedencia_sobre_selo():
    status = avalia_slide({"overflowY": 30, "overflowX": 0, "selos": 3})
    assert "overflow" in status


def test_resumo_conta_aprovacoes_e_falhas():
    assert resumo(["OK", "OK", "FALHA overflow y=1 x=0"]) == {"slides": 3, "ok": 2, "falhas": 1}
