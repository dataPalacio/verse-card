#!/usr/bin/env python3
r"""
Render Verse Card V5 - Warm Earth
Gera preview.html e PNGs 1080x1080 / 1080x1920 a partir de um content.json.

Estrutura de uma publicação:
    conteudos/publicados/<numero-tema>/publicacao/
      visualizar.html
      feed/slide-NN.png
      story/slide-NN.png
      relatorios/relatorio.md
      relatorios/relatorio.json

Uso preferencial (via wrapper, resolve interpretador e dependencias):
    .\executar.ps1 -Acao render -Conteudo conteudos/publicados/001-confiar-na-espera/conteudo.json

Uso direto:
    python -m sistema.pipeline.render conteudos/publicados/001-confiar-na-espera/conteudo.json [--saida PASTA]

A publicação salva os arquivos em `publicacao/`, ao lado do seu `conteudo.json`.
Use --saida apenas para testes ou experimentos.

Sai com codigo 1 se qualquer slide reprovar na auditoria.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from sistema.pipeline.auditoria import avalia_slide, resumo
from sistema.pipeline.construtores import render_slide
from sistema.pipeline.validacao import ErroDeConteudo, valida_conteudo
from sistema.pipeline.recursos import incorporar

RAIZ = Path(__file__).resolve().parent.parent.parent


def monta_documento(conteudo: dict) -> str:
    css = (RAIZ / "visual" / "modelo" / "carrossel.css").read_text(encoding="utf-8")
    logo = (RAIZ / "visual" / "marca" / "logo-base64.txt").read_text().strip()
    handle = conteudo.get("handle", "@sua.palavra.diaria")
    slides = "\n".join(render_slide(s, handle) for s in conteudo["slides"])
    titulo = conteudo.get("run_id", "Verse Card V5")
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="theme-color" content="#E8D5B7">
<title>{titulo}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
<style>{css.replace("__LOGO_B64__", logo)}</style></head><body>{slides}</body></html>"""


def caminho_arte(indice: int, slide: dict) -> str:
    """Caminho da arte relativo a publicacao: <formato>/slide-NN.png."""
    fmt = slide.get("formato", "feed")
    return f"{fmt}/slide-{indice:02d}.png"


def prepara_saida(saida: Path, slides: list) -> None:
    """Cria a estrutura da run e remove arte obsoleta de execucoes anteriores.

    Sem a limpeza, uma run que encolhe (8 slides -> 3) deixaria os PNGs 04..08
    da execucao anterior na pasta: o relatorio diria 3 e a pasta teria 8.
    """
    formatos = {s.get("formato", "feed") for s in slides}
    saida.mkdir(parents=True, exist_ok=True)
    for fmt in formatos:
        (saida / fmt).mkdir(parents=True, exist_ok=True)

    esperados = {saida / caminho_arte(i + 1, s) for i, s in enumerate(slides)}
    if saida.exists():
        for antigo in saida.glob("*/*.png"):
            if antigo not in esperados:
                antigo.unlink()
        # remove subpasta de formato que deixou de ser usado nesta run.
        # So as que nao pertencem a run atual: as dela nascem vazias aqui
        # e so recebem os PNGs depois, no screenshot.
        for sub in saida.iterdir():
            if sub.is_dir() and sub.name not in formatos and not any(sub.iterdir()):
                sub.rmdir()


def escreve_relatorios(saida: Path, conteudo: dict, linhas: list):
    """Relatorio humano (.md) e o mesmo dado em forma diffavel (.json)."""
    relatorios = saida / "relatorios"
    relatorios.mkdir(exist_ok=True)
    (relatorios / "relatorio.md").write_text(
        "# Relatorio de Render\n\n" + "\n".join(f"- {l['arquivo']}: {l['status']}" for l in linhas) + "\n",
        encoding="utf-8")
    totais = resumo([l["status"] for l in linhas])
    dados = {
        "run_id": conteudo.get("run_id"),
        "gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "OK" if totais["falhas"] == 0 else "FALHA",
        "totais": totais,
        "slides": linhas,
    }
    (relatorios / "relatorio.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dados


def caminho_publicacao(caminho_conteudo: Path, run_id: str) -> Path:
    """Escolhe uma saída simples ao lado de publicações cadastradas."""
    pasta = caminho_conteudo.resolve().parent
    if caminho_conteudo.name == "conteudo.json" and pasta.parent.name == "publicados":
        return pasta / "publicacao"
    return RAIZ / ".tmp" / "previews" / run_id


def main():
    ap = argparse.ArgumentParser(description="Renderiza uma run do Verse Card V5.")
    ap.add_argument("conteudo", help="caminho do content.json")
    ap.add_argument("--saida", default=None,
                    help="pasta para teste (padrao: publicacao/ ao lado do conteudo)")
    args = ap.parse_args()

    caminho_conteudo = Path(args.conteudo)
    conteudo = json.loads(caminho_conteudo.read_text(encoding="utf-8"))

    # Validacao ANTES de criar qualquer pasta: nada de saida pela metade.
    try:
        valida_conteudo(conteudo)
    except ErroDeConteudo as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    saida = Path(args.saida) if args.saida else caminho_publicacao(caminho_conteudo, conteudo["run_id"])
    # Resolva os recursos antes de substituir uma run anterior.
    documento = incorporar(monta_documento(conteudo))
    prepara_saida(saida, conteudo["slides"])

    preview = saida / "visualizar.html"
    preview.write_text(documento, encoding="utf-8")
    print(f"preview: {preview}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright ausente - apenas o preview HTML foi gerado.", file=sys.stderr)
        sys.exit(1)

    linhas = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=1)
        pg.goto(preview.resolve().as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("""async () => {
            await document.fonts.ready;
            await Promise.all([...document.images].map(img => img.decode()));
            for (const [peso, familia] of [['900', 'Inter'], ['400', 'Playfair Display']]) {
                const carregadas = await document.fonts.load(`${peso} 38px "${familia}"`);
                if (!carregadas.length || carregadas.some(f => f.status !== 'loaded'))
                    throw new Error(`Fonte nao carregada: ${familia}`);
            }
        }""")

        # Auditoria de overflow e selo conforme regras/conferencia.md.
        medidas = pg.evaluate("""() => [...document.querySelectorAll('.slide')].map(s => {
            const c = s.querySelector('.card');
            return {overflowY: c.scrollHeight - c.clientHeight,
                    overflowX: s.scrollWidth - s.clientWidth,
                    selos: s.querySelectorAll('.selo').length};
        })""")

        for i, s in enumerate(conteudo["slides"]):
            arquivo = caminho_arte(i + 1, s)
            pg.locator(".slide").nth(i).screenshot(path=str(saida / arquivo))
            m = medidas[i]
            status = avalia_slide(m)
            linhas.append({"indice": i + 1, "arquivo": arquivo, "formato": s.get("formato", "feed"),
                           "tipo": s["tipo"], "overflowY": m["overflowY"],
                           "overflowX": m["overflowX"], "selos": m["selos"], "status": status})
            print(f"  {arquivo} - {status}")
        b.close()

    dados = escreve_relatorios(saida, conteudo, linhas)
    print(f"relatorio: {saida / 'relatorios' / 'relatorio.md'}")
    if dados["status"] != "OK":
        print(f"\nRun REPROVADA: {dados['totais']['falhas']} slide(s) com falha.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
