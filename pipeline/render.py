#!/usr/bin/env python3
r"""
Render Verse Card V5 - Warm Earth
Gera slides.html (preview) e PNGs 1080x1080 / 1080x1920 a partir de um content.json.

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


def escreve_relatorios(saida: Path, conteudo: dict, linhas: list):
    """Relatorio humano (.md) e o mesmo dado em forma diffavel (.json)."""
    (saida / "render-report.md").write_text(
        "# Render Report\n\n" + "\n".join(f"- {l['arquivo']}: {l['status']}" for l in linhas) + "\n",
        encoding="utf-8")
    totais = resumo([l["status"] for l in linhas])
    dados = {
        "run_id": conteudo.get("run_id"),
        "gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "OK" if totais["falhas"] == 0 else "FALHA",
        "totais": totais,
        "slides": linhas,
    }
    (saida / "render-report.json").write_text(
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
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "slides-rendered").mkdir(exist_ok=True)

    preview = saida / "slides.html"
    preview.write_text(monta_documento(conteudo), encoding="utf-8")
    print(f"preview: {preview}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright ausente - apenas o preview HTML foi gerado.")
        return

    linhas = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=1)
        pg.goto(preview.resolve().as_uri())
        pg.wait_for_load_state("networkidle")
        pg.wait_for_timeout(2500)

        # auditoria de overflow - regra do render-quality-checklist
        medidas = pg.evaluate("""() => [...document.querySelectorAll('.slide')].map(s => {
            const c = s.querySelector('.card');
            return {overflowY: c.scrollHeight - c.clientHeight,
                    overflowX: s.scrollWidth - s.clientWidth,
                    selos: s.querySelectorAll('.selo').length};
        })""")

        for i, s in enumerate(conteudo["slides"]):
            nome = f"slide-{i+1:02d}-{s.get('formato','feed')}.png"
            pg.locator(".slide").nth(i).screenshot(path=str(saida / "slides-rendered" / nome))
            m = medidas[i]
            status = avalia_slide(m)
            linhas.append({"indice": i + 1, "arquivo": nome, "formato": s.get("formato", "feed"),
                           "tipo": s["tipo"], "overflowY": m["overflowY"],
                           "overflowX": m["overflowX"], "selos": m["selos"], "status": status})
            print(f"  {nome} - {status}")
        b.close()

    dados = escreve_relatorios(saida, conteudo, linhas)
    print(f"relatorio: {saida / 'render-report.md'}")
    if dados["status"] != "OK":
        print(f"\nRun REPROVADA: {dados['totais']['falhas']} slide(s) com falha.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
