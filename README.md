# Verse Card V5 — Warm Earth

Framework de geração de artes para o perfil **@sua.palavra.diaria**.
Capa em formato "cartão editorial": referência bíblica como herói tipográfico,
foto encaixada, passagem com numeração versicular.

Formatos suportados: **feed 1080×1080** e **story 1080×1920**.

---

## Tradução bíblica

Toda pesquisa e citação deve usar exclusivamente a **NTLH**. Conferir a versão
e a redação na fonte e registrar o link na nota editorial. Regra completa em
[regras/pesquisa-biblica.md](regras/pesquisa-biblica.md). Exemplos anteriores
são históricos; suas citações precisam ser conferidas em NTLH antes de reutilização.

## Estrutura

```text
verse-card-v5/
  executar.ps1                  entrada única de execução
  CLAUDE.md                     regras operacionais (agentes e contribuidores)
  requirements.txt              dependências com versão fixada

  conteudo/                     ENTRADAS
    proverbios-19-21.json
    exemplos/exemplo-minimo.json

  esquemas/
    content.schema.json         contrato do content.json

  pipeline/                     CÓDIGO
    render.py                   orquestração + Playwright
    recursos.py                 incorpora fontes e fotos no preview
    construtores.py             funções puras de HTML
    validacao.py                validação com mensagens em pt-BR
    validar.py                  valida sem renderizar
    auditoria.py                critérios de aprovação
    sincroniza_template.py      regenera os artefatos derivados

  template/
    verse-card.css              CSS canônico — fonte única de verdade
    verse-card-v5.html          preview autocontido — GERADO, não editar

  marca/
    logo-marca-warm-earth.png   selo 512×512, traço #5C3D1E — canônico
    logo-base64.txt             mesmo selo em base64 — GERADO do PNG

  artes/                        PNGs validados (referência visual, versionados)
  regras/                       regras de marca, qualidade e anti-patterns
  testes/                       52 testes, rodam sem browser

  saida/                        runs geradas (uma pasta por run_id) — não versionado
  .tmp/                         rascunho e intermediários — não versionado
```

`template/verse-card.css` é o único lugar onde tokens visuais são definidos.
O HTML autocontido é **gerado** a partir dele — se divergir, `-Acao verificar` falha.

---

## Instalação

```powershell
.\executar.ps1 -Acao preparar
```

Instala as dependências de `requirements.txt` e baixa o Chromium do Playwright.

---

## Como gerar uma run

```powershell
.\executar.ps1 -Acao render -Conteudo conteudo/proverbios-19-21.json
```

A pasta de saída vem do `run_id` do próprio conteúdo:

```text
saida/2026-09-01-proverbios-19-21-proposito/
  preview.html                preview navegável
  artes/
    feed/
      slide-01-feed.png
      slide-03-feed.png
      ...
    story/
      slide-02-story.png
  relatorio.md                auditoria legível
  relatorio.json              mesma auditoria, diffável entre runs
```

O render valida a entrada **antes** de escrever qualquer arquivo, confere se o
template está em sincronia com o CSS, e **sai com código 1** se algum slide
reprovar por overflow ou por contagem de selo.

Fontes e fotos HTTPS são baixadas pelo Python (respeitando o proxy do ambiente)
e incorporadas ao `preview.html`. As fotos externas precisam ser JPEG, PNG ou
WebP. O HTML entregue abre sem internet. Os downloads ficam em `.tmp/recursos/`;
remova esse cache para atualizar um recurso remoto que mudou mantendo a URL.
A primeira execução precisa de acesso às fontes e fotos. Falhas de download,
decodificação de imagem ou carregamento das fontes interrompem a execução.

## Piloto editorial em revisão

Tema 01: **Confiar durante a espera**, seis slides de feed, capa em Salmo 27:14
(NTLH) e reflexão contextual em Salmo 27. Execute:

```powershell
.\executar.ps1 -Acao render -Conteudo conteudo/salmo-27-espera.json
```

O texto da legenda está em `conteudo/salmo-27-espera-legenda.md`. Os dez temas
aprovados e a sequência de validação estão em `conteudo/temas-aprovados.md`.
Neste piloto, a legenda é produzida editorialmente após a revisão das artes;
o renderizador ainda não gera ou copia legendas automaticamente.

## Outros comandos

```powershell
.\executar.ps1 -Acao validar -Conteudo conteudo/<arquivo>.json   # só valida
.\executar.ps1 -Acao verificar                                   # testes + drift, sem browser
.\executar.ps1 -Acao sincronizar                                 # regenera derivados
.\executar.ps1 -Acao testar                                      # pytest
```

---

## Formato do content.json

Contrato completo em [esquemas/content.schema.json](esquemas/content.schema.json).

```jsonc
{
  "run_id": "2026-09-01-isaias-coisa-nova",   // AAAA-MM-DD-identificador; vira a pasta de saída
  "handle": "@sua.palavra.diaria",
  "slides": [
    {
      "tipo": "capa",              // "capa" | "interno"
      "formato": "feed",           // "feed" | "story"
      "livro": "Isaías",
      "referencia": "43:18–19",
      "foto": "https://…",         // opcional; sem foto = fundo gradiente
      "foto_alt": "descrição",     // obrigatório quando há foto
      "versiculos": [
        { "n": "18", "linhas": ["primeira linha", "linha indentada", "…"] }
      ],
      "hint": "arraste"
    },
    {
      "tipo": "interno",
      "formato": "feed",
      "titulo": "Uma coisa nova",
      "paragrafos": ["…", "…"],
      "marca_dagua": true,         // só no slide de fechamento
      "hint": "arraste"
    }
  ]
}
```

A primeira string de `linhas` fica alinhada ao número do versículo.
As demais recebem indentação francesa automática.

Conteúdo inválido é reprovado antes de gerar qualquer arquivo, com todos os
erros de uma vez:

```text
Conteudo invalido - 2 erro(s):
  - slides[3]: exige o campo "titulo" (obrigatorio para esse tipo de slide)
  - slides[5].versiculos[0].linhas: precisa de pelo menos 1 item(ns), veio vazio
```

---

## Tokens visuais

| Token | Valor | Uso |
| --- | --- | --- |
| `--bg-card` | `#F7F0E6` | Cartão |
| `--bg-outer-a` → `--bg-outer-b` | `#E8D5B7` → `#DCC49F` | Fundo do canvas |
| `--terracota` | `#C47B3A` | Referência versicular, números |
| `--marrom-escuro` | `#2E1A0E` | Nome do livro, títulos |
| `--marrom` | `#5C3D1E` | Corpo do texto bíblico |
| `--marrom-suave` | `#8B5F47` | Rodapé |
| `--hairline` | `rgba(196,123,58,.28)` | Divisor do rodapé |

Tipografia: **Inter 900** para o nome do livro, **Playfair Display** para o texto bíblico.

---

## Regras estruturais travadas

1. **Selo no rodapé, extremidade inferior direita.** Uma ocorrência por arte,
   34px no feed e 44px no story. Detalhes em [regras/brand-mark-rules.md](regras/brand-mark-rules.md).
2. **Nome de livro acima de 9 caracteres** recebe a classe `.longo`
   (104px → 76px), aplicada automaticamente.
3. **Story respeita safe areas do Instagram:** 220px no topo, 250px na base.
4. **Foto é elástica** (`flex: 1 1 auto`), a passagem não encolhe.
   Passagem longa reduz a foto, nunca estoura o cartão.
5. **Sem contador de slide** nas imagens — ver [regras/anti-patterns.md](regras/anti-patterns.md).

Critérios de aprovação de uma run em [regras/render-quality-checklist.md](regras/render-quality-checklist.md).

---

## Ponto aberto

Slides internos com pouco texto deixam vazio no terço inferior. O corpo já foi
elevado para 38px e a passagem é centralizada verticalmente no espaço livre,
mas passagens muito curtas ainda desequilibram.
