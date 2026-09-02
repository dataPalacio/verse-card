# Changelog

## Reestruturação — 2026-09-02

Organização do projeto. Nenhuma mudança de design: as artes são visualmente
idênticas às do V5 (diferença máxima de 5 níveis em 255, restrita à área do
selo, por regeneração do base64 a partir do PNG canônico de 512×512).

**Estrutura**

- Repositório próprio do projeto. Antes o `git rev-parse` apontava para
  `C:\Users\gusta` — um repositório acidental sobre a pasta pessoal inteira,
  sem `.gitignore`, com `.ssh/` e `.claude.json` no escopo.
- `.gitignore` separando fonte de artefato: `saida/` e `.tmp/` fora,
  `artes/` dentro (referência validada, não reproduzível por comando).
- Entradas movidas para `conteudo/`, separadas do código.
- `.tmp/` como destino declarado de rascunho. Removido `.superdesign/`,
  que era despejo de ferramenta externa na raiz.

**Execução**

- `executar.ps1` como entrada única. Resolve o interpretador (o README mandava
  usar `python3`, que nesta máquina é o stub da Microsoft Store) e encadeia
  validar → conferir sincronia → renderizar.
- `requirements.txt` com versões fixadas.

**Entradas**

- `esquemas/content.schema.json` e validação que reporta todos os erros de uma
  vez em pt-BR, ancorados no índice do slide.
- Validação roda ANTES do `mkdir`: conteúdo inválido não deixa mais pasta de
  saída pela metade. `versiculos[].linhas` vazia, que estourava `IndexError`
  no meio do render, virou mensagem de erro.

**Saídas**

- Pasta derivada do `run_id` (`saida/<run_id>/`). Antes o caminho vinha do argv
  e o `run_id` era decoração — nada garantia que concordassem.
- `render-report.json` ao lado do `.md`, com os números crus para diff entre runs.
- **Exit code 1** quando a auditoria reprova. Antes o relatório dizia FALHA e o
  processo saía com sucesso, apesar do README afirmar o contrário.

**Anti-drift**

- `template/verse-card-v5.html` passou a ser gerado de `verse-card.css`.
  Estava sem as regras `.passage-interno` havia uma versão inteira, enquanto o
  README afirmava que os dois estavam em sincronia.
- `marca/logo-base64.txt` passou a ser gerado do PNG. Os dois divergiam: o
  `.txt` guardava um downscale de 256×256 do asset de 512×512.

**Testes e regras**

- 40 testes que rodam sem browser (construtores, auditoria, validação, sincronia).
  `avalia_slide()` extraída do `main()` para ser testável isoladamente.
- `regras/brand-mark-rules.md` reescrito: descrevia o V4 (quatro classes de
  ancoragem, tamanhos 104/132/56/120px) enquanto o CSS implementa apenas
  `.selo` a 34/44px. O checklist agora separa automático de conferência humana.
- Criados `regras/render-quality-checklist.md` e `regras/anti-patterns.md`,
  citados pelo código e pelo README desde o V5 mas nunca escritos.
- `CLAUDE.md` com as invariantes operacionais.

## V5 — 2026-09-01

Correções sobre V4, todas medidas em render Chromium real:

- **Overflow eliminado.** V4 estourava 94px na capa feed e 160px no slide interno.
  Causa: `.photo` com altura fixa somada a `.passage` com `flex:1` sem `min-height:0`.
  Agora a foto é elástica e a passagem não encolhe.
- **Colisão do selo resolvida.** Em V4 o selo sobrepunha a caixa do `<h1>`
  em 94px (feed) e 122px (story). O selo saiu do posicionamento absoluto e
  passou a viver como filho flex da linha de rodapé.
- **Marca d'água não infla mais o canvas.** `bottom:-170px` adicionava 170px
  ao `scrollHeight`. Trocado por wrapper com `overflow:hidden`.
- **Safe areas do story.** Padding de 220px/250px; antes o rodapé ficava sob a UI.
- **Nome de livro longo.** Classe `.longo` reduz o corpo automaticamente.
- **Web Interface Guidelines:** dimensões explícitas em `<img>`, `alt`,
  `aria-label` no selo, `aria-hidden` na marca d'água, aspas curvas,
  `tabular-nums` nos números, `text-wrap:balance`, `translate="no"` no handle,
  `preconnect` das fontes, `theme-color`.

## V4 — 2026-09-01
Selo introduzido, formato story adicionado. Substituído por V5.

## V3 — 2026-09-01
Primeiro protótipo do formato cartão editorial.
