"""Regressoes: nao entregar foto quebrada nem HTML dependente da rede."""
import pytest
from sistema.pipeline import recursos


def test_preview_incorpora_fontes_e_foto(monkeypatch):
    respostas = {
        recursos.FONTES_URL: b'@font-face{src:url(https://exemplo.org/fonte.ttf)}',
        'https://exemplo.org/fonte.ttf': b'fonte-teste',
        'https://exemplo.org/foto?a=1&b=2': b'\xff\xd8\xfffoto-teste',
    }
    monkeypatch.setattr(recursos, 'baixar', respostas.__getitem__)
    original = ('<head><link href="' + recursos.FONTES_URL + '"></head>'
                '<img src="https://exemplo.org/foto?a=1&amp;b=2" alt="Lago">')
    resultado = recursos.incorporar(original)
    assert 'https://' not in resultado
    assert 'data:image/jpeg;base64,' in resultado
    assert 'alt="Lago"' in resultado
    assert 'data:application/octet-stream;base64,' in resultado


def test_resposta_html_no_lugar_da_foto_reprova(monkeypatch):
    monkeypatch.setattr(recursos, 'baixar', lambda url: b'<html>Erro</html>')
    with pytest.raises(ValueError, match='JPEG, PNG ou WebP'):
        recursos.incorporar('<head></head><img src="https://exemplo.org/foto">')


def test_falha_de_download_nao_e_silenciada(monkeypatch, tmp_path):
    monkeypatch.setattr(recursos, 'CACHE', tmp_path)
    def falhar(*args, **kwargs):
        raise TimeoutError('tempo esgotado')
    monkeypatch.setattr(recursos, 'urlopen', falhar)
    with pytest.raises(RuntimeError, match='Nao foi possivel carregar'):
        recursos.baixar('https://exemplo.org/foto')
    assert list(tmp_path.iterdir()) == []
