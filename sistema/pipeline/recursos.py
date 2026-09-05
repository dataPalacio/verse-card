"""Incorpora fontes e fotos no preview, respeitando o proxy do ambiente."""
import base64
import hashlib
import html
import re
from pathlib import Path
from urllib.request import urlopen

FONTES_URL = ('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900'
              '&family=Playfair+Display:wght@400;700&display=swap')
CACHE = Path(__file__).resolve().parent.parent.parent / '.tmp' / 'recursos'


def baixar(url: str) -> bytes:
    if not url.startswith('https://'):
        raise ValueError('Recurso externo precisa usar HTTPS.')
    CACHE.mkdir(parents=True, exist_ok=True)
    destino = CACHE / hashlib.sha256(url.encode()).hexdigest()
    if destino.exists():
        return destino.read_bytes()
    try:
        with urlopen(url, timeout=45) as resposta:
            dados = resposta.read()
        if not dados:
            raise ValueError('Resposta vazia.')
    except Exception as exc:
        raise RuntimeError(f'Nao foi possivel carregar recurso: {url}') from exc
    destino.write_bytes(dados)
    return dados


def uri(dados: bytes, mime: str) -> str:
    return f'data:{mime};base64,' + base64.b64encode(dados).decode('ascii')


def incorporar(documento: str) -> str:
    fontes = baixar(FONTES_URL).decode('utf-8')
    def fonte(match):
        url = match.group(1)
        return 'url(' + uri(baixar(url), 'application/octet-stream') + ')'
    fontes = re.sub(r'url\((https://[^)]+)\)', fonte, fontes)
    documento = re.sub(r'<link[^>]+href="https://fonts\.(?:googleapis|gstatic)\.com[^>]*>',
                       '', documento)
    documento = documento.replace('</head>', f'<style>{fontes}</style></head>')

    def foto(match):
        url = html.unescape(match.group(1))
        if url.startswith('data:image/'):
            return match.group(0)
        dados = baixar(url)
        if dados.startswith(b'\xff\xd8\xff'):
            mime = 'image/jpeg'
        elif dados.startswith(b'\x89PNG\r\n\x1a\n'):
            mime = 'image/png'
        elif dados[:4] == b'RIFF' and dados[8:12] == b'WEBP':
            mime = 'image/webp'
        else:
            raise ValueError('Foto precisa ser JPEG, PNG ou WebP valido.')
        return '<img src="' + uri(dados, mime) + '"'
    return re.sub(r'<img src="([^"]+)"', foto, documento)
