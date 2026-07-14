# Ad Editing QC

Guia curto para manter consistencia na decupagem de anuncios em `Lead -> Body -> CTA`.

## Objetivo

Ao editar um anuncio, o alvo nao e "encurtar o video". O alvo e isolar a copy vendavel, removendo:

- direcao de cena
- conversa com equipe
- reset de fala
- hesitacao abortada
- repeticao acidental
- silencio morto

Sem remover a estrutura comercial do anuncio.

## Regra Principal

Nao trocar o hook original por um lead "mais limpo" sem confirmar que a copy continua inteira.

Se o anuncio abre com um hook forte como:

- "Esse e o preco..."
- "Ta vendo?"
- "Nao da para..."

Esse hook precisa ser preservado se for parte real da copy, mesmo que exista outro trecho mais limpo depois.

## Estrutura Esperada

Antes de renderizar, mapear explicitamente:

1. Hook
2. Lead
3. Body
4. Proof
5. CTA

Se qualquer uma dessas partes estiver faltando, a versao esta incompleta.

## O Que Verificar No Transcript

Marcar como risco alto:

- frases interrompidas como `cria--`
- reinicios imediatos da mesma frase
- duplicacao semantica em janelas curtas
- CTA repetido em duas tomadas seguidas
- copy que reaparece com wording quase igual 2 a 5 segundos depois

Sempre que aparecer:

- `Pera ai`
- `Ta`
- `Entao`
- `Como eles conseguem...`
- `Eles tem bastante...`

verificar se isso e copy final ou apenas preparacao para uma retomada.

## Regra De Corte Para Frases Reiniciadas

Se uma frase comeca, quebra, e depois recomeça limpa, nunca manter as duas.

Escolher apenas um dos dois:

- a versao completa e limpa
- ou a versao curta, se a retomada nao acrescenta nada

Nunca concatenar "meio pensamento" com a versao refeita se isso produzir eco semantico.

## QC Obrigatorio Antes De Aprovar

Nao basta verificar:

- flash visual
- salto de quadro
- pop de audio

Tambem precisa haver QC semantico da copy.

Checklist obrigatorio:

1. Ler o EDL em ordem e confirmar `Hook -> Lead -> Body -> Proof -> CTA`.
2. Conferir cada bloco contra o transcript bruto.
3. Escutar especialmente as transicoes do fechamento.
4. Procurar duplicacao literal ou quase literal no ultimo terco do anuncio.
5. Confirmar que o CTA aparece uma vez so, a menos que a repeticao seja intencional.

## Heuristica Para Fechamento

Se o fechamento tiver:

- uma prova social
- uma frase abortada
- uma retomada da prova
- um CTA final

o default e:

- manter a prova limpa
- cortar a frase abortada inteira
- manter um unico CTA limpo

## Sinais De Erro Editorial

Se o usuario reagir com algo como:

- "sumiu metade do anuncio"
- "so tem metade da copy"
- "ta repetindo"
- "esse final ta errado"

assuma primeiro erro de selecao editorial, nao erro de render.

## Aprendizado Do Caso Ad9885

O que deu errado:

- o hook original "Esse e o preco..." foi removido
- um lead secundario foi promovido para abertura
- o fechamento preservou uma ideia dita duas vezes

O que passa a ser regra:

- manter o hook original quando ele faz parte da promessa comercial
- nao aprovar fechamento sem verificar duplicacao semantica no audio renderizado
- quando houver duvida no final, preferir entrar direto no CTA limpo

