# CLAUDE.md — verse-card-v5

Regras operacionais para agentes e contribuidores.
Complementa o `README.md` (o que é e como usar) e `regras/` (regras de arte).

---

## Pesquisa bíblica obrigatória

Usar exclusivamente NTLH em pesquisas, leitura de contexto e citações bíblicas.
Ler e aplicar `regras/pesquisa-biblica.md` antes de produzir ou revisar conteúdo.
Não substituir por outra tradução quando a fonte NTLH estiver indisponível.

## Idioma

Documentação, nomes de pasta e identificadores em **pt-BR**. Não traduzir
`saida`, `conteudo`, `regras`, `marca`, `artes`, nem os identificadores
`bloco_*`, `render_slide`, `avalia_slide`, `valida_conteudo`.
Mensagens de erro ao usuário também em pt-BR.

## Como rodar

Sempre pelo wrapper:

```powershell
.\executar.ps1 -Acao preparar                                        # deps + chromium
.\executar.ps1 -Acao validar -Conteudo conteudo/<arquivo>.json       # só valida
.\executar.ps1 -Acao render  -Conteudo conteudo/<arquivo>.json       # gera a run
.\executar.ps1 -Acao testar                                          # pytest
.\executar.ps1 -Acao sincronizar                                     # regenera derivados
.\executar.ps1 -Acao verificar                                       # testes + drift
```

**Nunca use `python3`** — nesta máquina é o stub da Microsoft Store, não um
interpretador. O wrapper resolve isso sozinho (`py -3`, senão `python`).

Não invoque `pipeline/render.py` como caminho solto; ele é um módulo de pacote
(`python -m pipeline.render`). O wrapper também garante a ordem correta:
validar → conferir sincronia → renderizar.

## Fonte de verdade

| Arquivo | Papel |
| --- | --- |
| `template/verse-card.css` | **canônico** — todos os tokens visuais nascem aqui |
| `template/verse-card-v5.html` | **gerado** — não editar à mão |
| `marca/logo-marca-warm-earth.png` | **canônico** — o selo |
| `marca/logo-base64.txt` | **gerado** do PNG — não editar à mão |
| `esquemas/content.schema.json` | contrato do `content.json` |

Editou o CSS ou o PNG? Rode `-Acao sincronizar`.

## Entradas e saídas

- Entradas ficam em `conteudo/`. Fixtures de exemplo em `conteudo/exemplos/`.
- A pasta de saída é **derivada do `run_id`**: `saida/<run_id>/`.
  Não passe `--saida` a não ser para experimento fora da convenção.
- Toda run gera `preview.html`, `artes/<formato>/slide-NN-<formato>.png`,
  `relatorio.md` e `relatorio.json`.
- As artes ficam separadas por formato: `artes/feed/` e `artes/story/`.
  Cada render limpa arte obsoleta da execucao anterior — a pasta sempre
  reflete exatamente o que o relatorio diz.

## Arquivos temporários

Tudo que for rascunho, intermediário ou descartável vai em `.tmp/`.
**Nunca crie pasta nova na raiz do projeto** — foi assim que `.superdesign/`
apareceu ali.

## Nunca commitar

`saida/`, `.tmp/`, `__pycache__/`, `.pytest_cache/`. Já cobertos pelo
`.gitignore`.

`artes/` **é** versionada: é referência visual validada, não reproduzível por
comando. `saida/` não é, porque é reproduzível.

## Git — atenção

Existe um repositório acidental em `C:\Users\gusta` cobrindo a pasta pessoal
inteira, sem `.gitignore`, com `.ssh/` e `.claude.json` no escopo.
O projeto tem repositório próprio desde 2026-09-02, que tem precedência.

Antes de qualquer commit:

```bash
git rev-parse --show-toplevel   # tem que responder .../verse-card-v5
```

Se apontar para fora do projeto, **pare** — um `git add -A` ali commitaria
dados pessoais do usuário.

## Antes de dizer que terminou

```powershell
.\executar.ps1 -Acao verificar
```

Tem que passar. Se mexeu em layout, rode também um `-Acao render` e olhe a arte
— o portão automático valida estrutura, não julga estética.

## Ao mudar layout

1. Edite `template/verse-card.css`.
2. `-Acao sincronizar`.
3. `-Acao render` e compare a arte com `artes/` (referência validada).
4. Se mudou regra de marca, atualize `regras/brand-mark-rules.md` **na mesma
   passagem**. Documento que descreve design inexistente é pior que documento
   nenhum — foi o que aconteceu entre o V4 e o V5.
