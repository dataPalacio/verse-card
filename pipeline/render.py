#!/usr/bin/env python3
r"""
Render Verse Card V5 - Warm Earth
Gera preview.html e PNGs 1080x1080 / 1080x1920 a partir de um content.json.

Estrutura de uma run:
    saida/<run_id>/
      preview.html
      artes/feed/slide-NN-feed.png
      artes/story/slide-NN-story.png
      relatorio.md
      relatorio.json

Uso preferencial (via wrapper, resolve interpretador e dependencias):
    .\executar.ps1 -Acao render -Conteudo conteudo/proverbios-19-21.json

Uso direto:
    python -m pipeline.render conteudo/proverbios-19-21.json [--saida PASTA]

A pasta de saida e derivada do run_id do proprio conteudo (saida/<run_id>/).
Use --saida apenas para experimentos fora da convencao.

Sai com codigo 1 se qualquer slide reprovar na auditoria.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from pipeline.auditoria import avalia_slide, resumo
from pipeline.construtores import render_slide
from pipeline.validacao import ErroDeConteudo, valida_conteudo
from pipeline.recursos import incorporar

RAIZ = Path(__file__).resolve().parent.parent


def monta_documento(conteudo: dict) -> str:
    css = (RAIZ / "template" / "verse-card.css").read_text(encoding="utf-8")
    logo = (RAIZ / "marca" / "logo-base64.txt").read_text().strip()
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
    """Caminho da arte relativo a pasta da run: artes/<formato>/slide-NN-<formato>.png"""
    fmt = slide.get("formato", "feed")
    return f"artes/{fmt}/slide-{indice:02d}-{fmt}.png"


def prepara_saida(saida: Path, slides: list) -> None:
    """Cria a estrutura da run e remove arte obsoleta de execucoes anteriores.

    Sem a limpeza, uma run que encolhe (8 slides -> 3) deixaria os PNGs 04..08
    da execucao anterior na pasta: o relatorio diria 3 e a pasta teria 8.
    """
    artes = saida / "artes"
    formatos = {s.get("formato", "feed") for s in slides}
    saida.mkdir(parents=True, exist_ok=True)
    for fmt in formatos:
        (artes / fmt).mkdir(parents=True, exist_ok=True)

    esperados = {saida / caminho_arte(i + 1, s) for i, s in enumerate(slides)}
    if artes.exists():
        for antigo in artes.rglob("*.png"):
            if antigo not in esperados:
                antigo.unlink()
        # remove subpasta de formato que deixou de ser usado nesta run.
        # So as que nao pertencem a run atual: as dela nascem vazias aqui
        # e so recebem os PNGs depois, no screenshot.
        for sub in artes.iterdir():
            if sub.is_dir() and sub.name not in formatos and not any(sub.iterdir()):
                sub.rmdir()


def escreve_relatorios(saida: Path, conteudo: dict, linhas: list):
    """Relatorio humano (.md) e o mesmo dado em forma diffavel (.json)."""
    (saida / "relatorio.md").write_text(
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
    (saida / "relatorio.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dados


def main():
    ap = argparse.ArgumentParser(description="Renderiza uma run do Verse Card V5.")
    ap.add_argument("conteudo", help="caminho do content.json")
    ap.add_argument("--saida", default=None,
                    help="pasta de saida (padrao: saida/<run_id>)")
    args = ap.parse_args()

    conteudo = json.loads(Path(args.conteudo).read_text(encoding="utf-8"))

    # Validacao ANTES de criar qualquer pasta: nada de saida pela metade.
    try:
        valida_conteudo(conteudo)
    except ErroDeConteudo as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    saida = Path(args.saida) if args.saida else RAIZ / "saida" / conteudo["run_id"]
    # Resolva os recursos antes de substituir uma run anterior.
    documento = incorporar(monta_documento(conteudo))
    prepara_saida(saida, conteudo["slides"])

    preview = saida / "preview.html"
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

        # auditoria de overflow - regra do render-quality-checklist
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
    print(f"relatorio: {saida / 'relatorio.md'}")
    if dados["status"] != "OK":
        print(f"\nRun REPROVADA: {dados['totais']['falhas']} slide(s) com falha.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
