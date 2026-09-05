# Piloto 01 — Confiar durante a espera

- Versão: 3. Layout validado pelo Gustavo; citação atualizada para NTLH.
- Base: Salmo 27:13–14, com citação literal apenas de 27:14 na capa (NTLH).
- Formato: seis PNGs de feed, 1080 × 1080.
- Visual: template Warm Earth atual, foto já utilizada pelo repositório, logo canônica no rodapé; marca d'água apenas no fechamento.
- Sequência: passagem → identificação com a espera → contexto do salmo → coragem → aplicação → oração.
- Capa preserva o padrão bíblico do projeto. O gancho temático aparece no slide 02.

## Execução e correção encontrada

A primeira execução marcou os seis slides como OK, mas a inspeção visual
encontrou foto ausente e fontes substituídas. O portão anterior só conferia
overflow e quantidade de selos.

Foi acrescentada incorporação de fontes e fotos no HTML, usando o acesso HTTP
do Python e cache em `.tmp/recursos/`. Antes da captura, o browser agora aguarda
as fontes e a decodificação das imagens. Falta de Playwright também passa a
retornar código de erro. Na versão 1, não houve alteração no CSS canônico ou na logo.

Verificação: 52 testes aprovados e sincronia dos derivados conferida. A segunda
renderização gerou os seis PNGs com relatório OK. HTML autocontido entregue
com as fontes, a logo e a foto incorporadas.

Ambiente do piloto: Linux, Python 3.12, PowerShell 7.4.6 e Playwright 1.61.0.
Execução pelo `executar.ps1`. O download automático do Chromium falhou por
timeout; a mesma versão foi instalada pelo arquivo oficial do Chrome for
Testing no Google Storage, sem alterar as dependências do repositório.

## Pontos para retorno

1. A capa deve continuar priorizando livro/versículo ou ganhar gancho temático?
2. A quantidade de texto e a leitura nos slides internos estão adequadas?
3. O tom acolhedor e a oração representam o perfil?
4. A legenda complementa o carrossel como desejado?

## Git

Base do piloto: `main`, commit `095c810373883a3f1b3a195d28ed5b887acde08d`.
Trabalho preparado em `staging` local. O envio ao GitHub ocorrerá após os
refinamentos; PR de `staging` para `main` fica para a etapa posterior combinada.

## Revisão 2 — espaçamento dos títulos

Ajuste no CSS canônico dos títulos internos de feed: fonte de 76 para 68 px,
entrelinha de 0,94 para 1,16, espaçamento de letras de -0,035 para -0,015 em
e largura máxima de 740 px. Isso afasta as linhas e os acentos nos slides 2
e 6 e distribui o título do slide 4 em duas linhas. A regra vale para todos
os títulos internos de feed, mantendo consistência. Capa e story preservados.

Template derivado sincronizado, seis slides renderizados sem overflow e
52 testes aprovados. Slides 2, 4 e 6 inspecionados visualmente.

## Revisão 3 — NTLH exclusiva

Regra registrada em `regras/pesquisa-biblica.md` e vinculada no README e nas
instruções operacionais. Capa conferida em https://www.bible.com/pt/bible/211/PSA.27.14.NTLH.
Contexto conferido em https://www.bible.com/pt/bible/211/PSA.27.NTLH.
Slide 4 ajustado para falar em confiança e coragem, conforme a NTLH.
Layout da versão 2 preservado. Após a validação do usuário, alterações
consolidadas para envio à staging remota; PR permanece para a próxima etapa.
