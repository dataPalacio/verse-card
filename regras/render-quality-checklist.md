# Render Quality Checklist

Critérios de aprovação de uma run. Referenciado por `pipeline/render.py` e por
`regras/brand-mark-rules.md`.

> Este arquivo era citado pelo código e pela documentação desde o V5, mas nunca
> tinha sido criado. Existe desde a reestruturação de 2026-09-02.

---

## Portão automático

Roda em `pipeline/auditoria.py` sobre o DOM renderizado no Chromium. Qualquer
falha reprova a run inteira e faz o `render.py` **sair com código 1**.

| Critério | Medida | Limite |
| --- | --- | --- |
| Overflow vertical | `card.scrollHeight - card.clientHeight` | 0 |
| Overflow horizontal | `slide.scrollWidth - slide.clientWidth` | 0 |
| Ocorrências do selo | `slide.querySelectorAll('.selo').length` | exatamente 1 |

Overflow tem precedência sobre contagem de selo: um cartão que estoura invalida
a arte independentemente da marca.

Os números crus ficam registrados em `render-report.json`, não só o veredito.
Isso permite ver um slide passar de 0 para 3px de folga **antes** de virar falha
— um cartão que passou raspando hoje é o que estoura na próxima passagem longa.

## Portão sem browser

Roda em `.\executar.ps1 -Acao verificar`, em menos de um segundo:

- 40 testes unitários sobre construtores, auditoria, validação e sincronia;
- conferência de que `verse-card-v5.html` reflete `verse-card.css`;
- conferência de que `logo-base64.txt` corresponde ao PNG canônico.

## Portão de entrada

Antes de qualquer escrita em disco, `pipeline/validacao.py` valida o
`content.json` contra `esquemas/content.schema.json`. Conteúdo inválido sai com
código 2 e **não cria pasta de saída**.

Cobre, entre outros: `versiculos[].linhas` vazia (que antes estourava
`IndexError` no meio do render), `capa` sem `livro`, `interno` sem `paragrafos`,
`foto` sem `foto_alt`, e `run_id` fora do padrão `AAAA-MM-DD-identificador`.

---

## Conferência humana

O portão automático garante que a arte é **válida**, não que está **boa**.
Antes de publicar:

- [ ] o texto bíblico quebra em pontos que respeitam o sentido da frase
- [ ] a foto não corta elemento importante no `object-fit:cover`
- [ ] o contraste do texto sobre o cartão está confortável na tela do celular
- [ ] o terço inferior dos slides internos não ficou visivelmente vazio
- [ ] a numeração versicular corresponde à passagem citada
- [ ] o `hint` do último slide convida à ação certa ("salve para lembrar")

## Ponto aberto conhecido

Slides internos com pouco texto deixam vazio no terço inferior. O corpo já foi
elevado para 38px e o `.passage-interno` recebeu
`justify-content:center`, o que centraliza a passagem no espaço livre. Passagens
muito curtas ainda desequilibram. Não há verificação automática para isso —
permanece na conferência humana acima.
