# Organização de arquivos

Esta regra mantém o projeto simples para encontrar e criar publicações.

## Pastas

| Pasta | Uso |
| --- | --- |
| `conteudos/` | temas, publicações e exemplos de conteúdo |
| `visual/` | logo, modelo e exemplos visuais |
| `regras/` | regras para produzir e conferir conteúdos |
| `sistema/` | código e testes necessários para gerar as artes |

## Uma publicação por pasta

Crie a publicação em `conteudos/publicados/<numero>-<tema>/`.

Exemplo: `conteudos/publicados/001-confiar-na-espera/`.

Use sempre estes arquivos:

| Arquivo | Uso |
| --- | --- |
| `conteudo.json` | conteúdo dos slides usado pelo gerador |
| `legenda.txt` | legenda pronta para copiar e postar |
| `notas.md` | fonte NTLH, contexto, decisões e histórico de revisão |
| `publicacao/` | HTML, imagens e relatórios gerados; não editar nem versionar |

## Nomes

- Use letras minúsculas, números e hífens: `002-entregar-a-ansiedade`.
- Não use espaços, acentos, `final`, `novo`, `revisado` ou números de versão no nome da pasta.
- O número identifica o tema; a situação da publicação fica em `conteudos/planejamento.md`.
- As imagens usam `slide-01.png`, `slide-02.png` e assim por diante.
- Use `feed/` e `story/` somente dentro de `publicacao/`.

## Antes de produzir

1. Adicione ou atualize o tema em `conteudos/planejamento.md`.
2. Crie a pasta da publicação ao iniciar a produção.
3. Registre a fonte e a versão NTLH em `notas.md`.
4. Gere as artes pelo `executar.ps1`.
5. Atualize a situação no planejamento depois da validação.

Não deixe arquivos de uma publicação soltos fora da pasta dela. Conteúdos ainda não iniciados ficam apenas no planejamento.
