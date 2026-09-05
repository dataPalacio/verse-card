#!/usr/bin/env python3
r"""
Validacao do conteudo.json contra sistema/esquemas/content.schema.json.

Roda ANTES de qualquer escrita em disco: um conteudo invalido nao deve
deixar pasta de saida pela metade. Reporta TODOS os erros de uma vez,
traduzidos para pt-BR e ancorados no indice do slide.
"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

RAIZ = Path(__file__).resolve().parent.parent.parent
CAMINHO_SCHEMA = RAIZ / "sistema" / "esquemas" / "content.schema.json"


class ErroDeConteudo(Exception):
    """Conteudo reprovado na validacao. A mensagem ja vem formatada em pt-BR."""

    def __init__(self, problemas):
        self.problemas = problemas
        n = len(problemas)
        corpo = "\n".join(f"  - {p}" for p in problemas)
        super().__init__(f"Conteudo invalido - {n} erro(s):\n{corpo}")


def _caminho(erro) -> str:
    """slides/3/versiculos/0/linhas -> slides[3].versiculos[0].linhas"""
    partes = []
    for p in erro.absolute_path:
        if isinstance(p, int):
            partes[-1] = f"{partes[-1]}[{p}]" if partes else f"[{p}]"
        else:
            partes.append(str(p))
    return ".".join(partes) if partes else "(raiz)"


def _mensagem(erro) -> str:
    """Traduz o vocabulario do jsonschema para pt-BR."""
    k = erro.validator
    if k == "required":
        campo = str(erro.message).split("'")[1]
        # dentro de um if/then o contexto ja e o slide; deixa explicito o porque
        origem = erro.schema_path
        if "then" in list(origem):
            return f'exige o campo "{campo}" (obrigatorio para esse tipo de slide)'
        return f'falta o campo obrigatorio "{campo}"'
    if k == "minItems":
        minimo = erro.validator_value
        return f"precisa de pelo menos {minimo} item(ns), veio vazio"
    if k == "minLength":
        return "nao pode ser texto vazio"
    if k == "enum":
        return f"valor invalido; use um de: {', '.join(map(str, erro.validator_value))}"
    if k == "pattern":
        return ("formato invalido; use AAAA-MM-DD-identificador "
                "(minusculas, numeros e hifens)")
    if k == "type":
        return f"tipo invalido; esperado {erro.validator_value}"
    if k == "additionalProperties":
        return f"campo nao reconhecido - {erro.message}"
    return erro.message


def valida_conteudo(conteudo: dict) -> None:
    """Levanta ErroDeConteudo com todos os problemas encontrados."""
    schema = json.loads(CAMINHO_SCHEMA.read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    erros = sorted(v.iter_errors(conteudo), key=lambda e: list(e.absolute_path))
    if not erros:
        return
    problemas, vistos = [], set()
    for e in erros:
        texto = f"{_caminho(e)}: {_mensagem(e)}"
        if texto not in vistos:
            vistos.add(texto)
            problemas.append(texto)
    raise ErroDeConteudo(problemas)


def valida_arquivo(caminho) -> dict:
    conteudo = json.loads(Path(caminho).read_text(encoding="utf-8"))
    valida_conteudo(conteudo)
    return conteudo
