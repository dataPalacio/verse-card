# Anti-patterns

Erros já cometidos neste projeto, com a causa raiz. Cada item existe porque
custou uma versão ou um retrabalho.

> Citado pela regra 5 do `README.md` desde o V5, mas nunca criado.
> Existe desde a reestruturação de 2026-09-02.

---

## Arte

**Contador de slide na imagem.** Nada de "1/8" nas artes. O Instagram já mostra
a posição no carrossel; repetir isso rouba espaço e envelhece a arte quando a
sequência muda.

**Duas ocorrências do selo no mesmo canvas.** Reprova a run. A marca d'água é a
única exceção, e só no slide de fechamento ou CTA. Ver `brand-mark-rules.md`.

**Selo sobre foto, texto ou linha divisória.** No V5 isso é impossível por
construção — o selo vive no rodapé, que é faixa reservada. Qualquer proposta de
voltar a posicioná-lo de forma absoluta reabre a colisão de 94px do V4.

---

## CSS

**`.passage` com `flex:1` sem `min-height:0`.** Causa raiz do overflow do V4:
estourava 94px na capa feed e 160px no slide interno. Em um contêiner flex, o
`min-height` padrão é `auto`, o que impede o item de encolher abaixo do próprio
conteúdo. A foto é que deve ser elástica (`flex:1 1 auto`); a passagem não
encolhe.

**Altura fixa na foto somada a passagem flexível.** Mesma família do item
anterior. Passagem longa tem que reduzir a foto, nunca estourar o cartão.

**Elemento com deslocamento negativo sem wrapper que recorte.** O
`bottom:-170px` da marca d'água inflava o `scrollHeight` do cartão em 170px e
fazia a auditoria reprovar arte que estava visualmente correta. A solução é o
`.agua-wrap` com `overflow:hidden`.

**Definir token visual fora de `verse-card.css`.** O CSS é fonte única de
verdade. Cor, tamanho e espaçamento nascem lá.

---

## Pipeline

**Editar `template/verse-card-v5.html` à mão.** O arquivo é GERADO. Uma edição
manual é sobrescrita no próximo `-Acao sincronizar`, e antes disso faz o
`-Acao verificar` falhar. Mexa no `verse-card.css` e sincronize.

Foi exatamente o que aconteceu entre o V5 e a reestruturação: o template ficou
sem as regras `.passage-interno` por uma versão inteira, silenciosamente,
enquanto o README afirmava que os dois estavam em sincronia. Documentação não
impede divergência — só geração impede.

**Editar `marca/logo-base64.txt` à mão.** Também é gerado, a partir do PNG
canônico. Os dois chegaram a divergir: o `.txt` guardava um downscale de
256×256 enquanto o asset era 512×512.

**Criar pasta nova na raiz do projeto.** Rascunho e artefato intermediário vão
em `.tmp/`. Foi assim que `.superdesign/` acabou versionado junto do projeto.

**Escrever em disco antes de validar a entrada.** Deixa pasta de saída pela
metade quando o conteúdo está errado. A validação roda antes do `mkdir`.

**Informar a pasta de saída à mão.** Ela é derivada do `run_id`. Quando os dois
são independentes, nada garante que concordem — e o `run_id` do JSON vira
decoração. Use `--saida` apenas para experimento fora da convenção.

**Reprovar a run e sair com código 0.** Era o comportamento até a
reestruturação: o relatório dizia FALHA e o processo terminava com sucesso.
Falha tem que ser observável por quem chama.

---

## Git

**Rodar `git add -A` sem conferir o escopo do repositório.** Existe um `.git`
acidental em `C:\Users\gusta` cobrindo a pasta pessoal inteira, sem
`.gitignore`. Antes de qualquer commit, confirme:

```bash
git rev-parse --show-toplevel   # tem que apontar para verse-card-v5
```

**Versionar `saida/`.** É artefato reproduzível a partir de `conteudo/` +
`template/`. `artes/` é diferente: é referência visual validada, não
reproduzível por comando, e por isso é versionada.
