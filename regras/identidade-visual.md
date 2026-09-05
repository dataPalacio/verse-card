# Brand Mark Rules — Selo @sua.palavra.diaria

**Squad:** carrossel-biblico-ig
**Asset canônico:** `visual/marca/logo.png` (512×512, PNG transparente, traço em `#5C3D1E`)
**Derivado:** `visual/marca/logo-base64.txt` — gerado do PNG por `.\executar.ps1 -Acao sincronizar`. Não editar à mão.
**Aplica-se a:** todas as artes de feed (1080×1080) e story (1080×1920).

> **Estado deste documento.** Até a reestruturação de 2026-09-02 este arquivo
> descrevia o layout do V4 (selo em posicionamento absoluto, quatro classes de
> ancoragem). O V5 mudou a estrutura e o documento não acompanhou. As regras
> abaixo refletem o que o CSS realmente implementa — conferidas contra
> `visual/modelo/carrossel.css`.

---

## Regra 1 — O selo é obrigatório e único

Toda arte gerada pelo pipeline carrega o selo. **Uma única ocorrência visível por arte.**
Duas aplicações no mesmo canvas é erro de render e reprova a run.

Exceção: a marca d'água (`.selo-agua`) não conta como ocorrência e pode coexistir
com o selo, desde que apenas no slide de fechamento ou CTA.

Verificação automática em dois níveis: o teste unitário
`test_slide_emite_exatamente_um_selo` trava a regra sem browser, e a auditoria
de render conta as ocorrências no DOM renderizado.

## Regra 2 — O selo vive no rodapé, como filho flex

O selo é o **último filho de `.foot .right`**, depois do texto de hint.
Não é posicionado de forma absoluta.

```html
<footer class="foot">
  <span class="brand">@sua.palavra.diaria</span>
  <span class="right"><span>arraste</span><span class="selo"></span></span>
</footer>
```

O rodapé é uma faixa reservada: tem `border-top`, `flex-shrink:0` e vive fora do
fluxo do conteúdo. **Por construção** o selo nunca cruza headline, foto ou corpo
de texto — não é uma regra a ser conferida no olho, é uma consequência do layout.

Foi exatamente essa a mudança do V4 para o V5. No V4 o selo era absoluto e
colidia com a caixa do `<h1>` em 94px no feed e 122px no story (ver `CHANGELOG.md`).

Existe **uma única classe de selo aplicado: `.selo`.** As classes
`.selo-topo-dir`, `.selo-rodape` e `.selo-story`, descritas em versões
anteriores deste documento, não existem no CSS e não devem ser usadas.

## Regra 3 — Tamanhos por contexto

Valores conforme `visual/modelo/carrossel.css`:

| Contexto | Seletor | Tamanho | Opacidade |
| --- | --- | --- | --- |
| Rodapé feed | `.selo` | 34 × 34 px | 0.85 |
| Rodapé story | `.story .selo` | 44 × 44 px | 0.85 |
| Marca d'água | `.agua-wrap .selo-agua` | 560 × 560 px | 0.05 |

Não escalar fora destes valores. Não aplicar sombra, moldura, fundo sólido ou rotação.

A marca d'água vive dentro de `.agua-wrap`, que tem `overflow:hidden`. O wrapper
existe porque o `bottom:-170px` do selo, sem recorte, inflava o `scrollHeight`
do cartão em 170px e fazia a auditoria de overflow reprovar a arte indevidamente.

## Regra 4 — Área de respiro

O respiro do selo é consequência do layout do rodapé, não um número a ser medido
manualmente:

- separação horizontal do texto de hint: `gap:18px` em `.foot .right`;
- separação vertical do conteúdo: `padding-top:18px` no feed, `26px` no story,
  somados ao `border-top` da faixa;
- distância da borda do cartão: o próprio padding do `.card` naquele contexto.

Mexer nesses valores é mexer no respiro do selo.

## Regra 5 — Cor

O selo usa o traço em `#5C3D1E` sobre fundos claros (`#F7F0E6`, `#E8D5B7`).
Sobre foto ou fundo escuro, usar a variante em `#F7F0E6` — nunca terracota
`#C47B3A`, reservada a acentos tipográficos e que perderia legibilidade no traço fino.

No layout atual o selo está sempre sobre o fundo claro do cartão, então a
variante clara não é exercitada pelo pipeline. Ela permanece documentada para
templates futuros que coloquem o selo sobre imagem.

## Regra 6 — Safe areas do story

No formato 1080×1920, os 220 px superiores e os 250 px inferiores são zona de UI
do Instagram. O `.story` reserva essas faixas no próprio padding
(`padding:220px 52px 250px`), de modo que **todo o cartão** — e portanto o selo,
que vive dentro dele — já nasce fora da zona de UI.

Não existe `.selo-story` ancorado em `bottom:150px`; essa construção era do V4.

---

## Checklist

Automático — verificado pelo pipeline, reprova a run sozinho:

- [x] selo presente em todas as artes da run
- [x] uma única ocorrência do selo por arte
- [x] cartão sem overflow vertical ou horizontal
- [x] `logo-base64.txt` em sincronia com o PNG canônico

Manual — conferência humana antes de publicar:

- [ ] traço legível sobre o fundo daquela arte
- [ ] sem sombra, moldura, fundo sólido ou rotação aplicados ao selo
- [ ] marca d'água apenas no slide de fechamento ou CTA

Distinguir os dois blocos é o que impede este documento de voltar a descrever
um design que não existe: o que é automático está travado por teste, o que é
manual está explicitamente marcado como responsabilidade de quem publica.
