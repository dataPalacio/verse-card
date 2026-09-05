# Instruções do projeto

## Regras obrigatórias

- Leia e aplique `regras/organizacao.md` antes de criar, mover ou renomear arquivos.
- Leia e aplique `regras/pesquisa-biblica.md` antes de produzir ou revisar conteúdo bíblico. A NTLH é a única tradução permitida.
- Use nomes em português, minúsculos, sem acentos e separados por hífens.
- Uma publicação fica inteira em `conteudos/publicados/<numero>-<tema>/`.
- Não edite arquivos em `publicacao/`: eles são gerados pelo renderizador.

## Execução

Sempre execute pelo wrapper:

```powershell
.\executar.ps1 -Acao preparar
.\executar.ps1 -Acao validar -Conteudo conteudos/publicados/<numero>-<tema>/conteudo.json
.\executar.ps1 -Acao render -Conteudo conteudos/publicados/<numero>-<tema>/conteudo.json
.\executar.ps1 -Acao sincronizar
.\executar.ps1 -Acao verificar
```

Não invoque arquivos de `sistema/pipeline/` diretamente.

## Fontes de verdade

| Arquivo | Função |
| --- | --- |
| `visual/modelo/carrossel.css` | Cores, fontes, tamanhos e espaçamentos |
| `visual/modelo/carrossel.html` | Arquivo gerado; não editar à mão |
| `visual/marca/logo.png` | Logo original |
| `visual/marca/logo-base64.txt` | Arquivo gerado a partir da logo |
| `sistema/esquemas/content.schema.json` | Formato válido de `conteudo.json` |

Depois de alterar o CSS ou a logo, rode `-Acao sincronizar`. Antes de concluir qualquer mudança, rode `-Acao verificar`. Se houver alteração visual, gere a publicação e inspecione as imagens.

## Arquivos temporários

Não versionar `publicacao/`, `.tmp/`, `__pycache__/` ou `.pytest_cache/`. Os exemplos em `visual/exemplos/` são referências visuais e devem permanecer versionados.
