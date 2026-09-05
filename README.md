# Sua Palavra Diária

Este projeto cria carrosséis bíblicos para o Instagram.

## Onde encontrar cada coisa

- `conteudos/planejamento.md`: lista de temas e situação de cada um.
- `conteudos/publicados/`: uma pasta para cada publicação aprovada.
- `conteudos/exemplos/`: exemplos para aprender ou testar o modelo.
- `visual/`: logo, modelo do carrossel e exemplos visuais.
- `regras/`: regras de conteúdo, pesquisa bíblica e identidade visual.
- `sistema/`: arquivos técnicos que geram e testam as publicações.

As regras de organização estão em [regras/organizacao.md](regras/organizacao.md). As citações bíblicas devem seguir [regras/pesquisa-biblica.md](regras/pesquisa-biblica.md): use somente a NTLH.

## Como criar ou atualizar uma publicação

1. Escolha um tema em `conteudos/planejamento.md`.
2. Crie uma pasta em `conteudos/publicados/` seguindo o padrão `001-nome-do-tema`.
3. Preencha `conteudo.json`, `legenda.txt` e `notas.md` nessa pasta.
4. Execute:

```powershell
.\executar.ps1 -Acao render -Conteudo conteudos/publicados/001-confiar-na-espera/conteudo.json
```

Os arquivos para postar aparecerão em `publicacao/`, dentro da pasta desse conteúdo:

```text
conteudos/publicados/001-confiar-na-espera/
  conteudo.json
  legenda.txt
  notas.md
  publicacao/
    visualizar.html
    feed/
      slide-01.png
    relatorios/
      relatorio.md
```

`publicacao/` é gerada novamente a cada execução e não é enviada ao GitHub.

## Comandos úteis

```powershell
.\executar.ps1 -Acao preparar
.\executar.ps1 -Acao validar -Conteudo conteudos/publicados/001-confiar-na-espera/conteudo.json
.\executar.ps1 -Acao render -Conteudo conteudos/publicados/001-confiar-na-espera/conteudo.json
.\executar.ps1 -Acao verificar
```

O modelo visual está em `visual/modelo/carrossel.css`. Depois de alterar o modelo ou a logo, execute:

```powershell
.\executar.ps1 -Acao sincronizar
```
