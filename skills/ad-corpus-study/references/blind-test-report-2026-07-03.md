# Blind Test Report - 2026-07-03

Objetivo: validar se as skills novas ajudam um subagente a editar anuncios sem contexto da conversa e identificar falhas reais do sistema.

## Casos

1. Video teste `Ad9885_esse e o preco...`
2. `9119`
3. `8263`
4. `8105`

## Protocolo

- o subagente recebeu apenas o bruto e as skills relevantes
- nao recebeu o `Final.txt` de referencia
- foi instruido a retornar:
  - `FINAL_COPY`
  - `DIFFICULTIES`
  - `RISK_NOTES`

## Resultado por caso

### Caso 1 - Video teste Ad9885

Resultado:

- o subagente preservou o hook visual `Esse e o preco...`
- removeu resets e ruido de set
- manteve a oferta e o CTA

Comparacao:

- ficou proximo da versao corrigida produzida na sessao principal
- nao repetiu o CTA
- ainda abriu com copy dependente de apoio visual, o que exige atencao editorial

Leitura:

- skills funcionaram bem nesse caso

### Caso 2 - 9119

Resultado:

- o subagente condensou bem um bruto baguncado e manteve a tese central
- trocou parte da especificidade da oferta por resumo mais generico

Comparacao com `Final.txt`:

- o `Final.txt` de referencia parece fraco/corrompido, com repeticao longa de `Adapta.org`
- neste caso, o subagente provavelmente produziu algo melhor que a referencia

Leitura:

- confirmacao de que nem todo `Final.txt` deve ser tratado como gold absoluto

### Caso 3 - 8263

Resultado:

- boa limpeza de repeticao
- manteve a estrutura comercial
- suavizou a agressividade da performance

Comparacao com `Final.txt`:

- semanticamente proximo
- menos punch em fragmentos como `Oitavo!`, `Free.`, `Exato.`

Leitura:

- falha parcial: o sistema tende a normalizar demais a voz

### Caso 4 - 8105

Resultado:

- muito proximo da referencia
- bom controle de segredo, escassez e CTA

Comparacao com `Final.txt`:

- pouca diferenca funcional
- perda pequena de intensidade no fechamento

Leitura:

- skills funcionam bem quando o bruto ja vem quase limpo

## Padrões observados

### O sistema foi bem em:

- cortar reset e meta-fala
- remover repeticao literal
- preservar arco comercial
- identificar riscos de claim/compliance

### O sistema ainda falhava em:

- abstrair demais detalhes concretos da oferta
- neutralizar excessivamente a voz de performance
- presumir que referencias finais do corpus sao sempre ouro

## Mudancas feitas apos o blind test

- reforco para preservar detalhes concretos de oferta
- reforco para nao achatar fragmentos de performance que vendem
- reforco para tratar `Final.txt` como referencia util, mas falivel

## Decisao

Blind test aprovou o sistema como base util para decupagem, mas nao como piloto automatico.

Uso recomendado:

- agente continua sendo o editor
- tools e skills devem apoiar
- QC semantico continua obrigatorio antes de aprovar saida final

## Round 2

Segunda rodada cega com:

1. video teste `Ad9885_esse e o preco...`
2. `8262`
3. `8834`
4. `9303`

### Resultado resumido

- `8262`: muito proximo da referencia, e ainda removeu uma duplicacao residual de `Entao faz o seguinte`.
- `9303`: muito proximo da referencia e preservou bem a analogia Red Bull + oferta + prerequisito.
- `8834`: baixa similaridade textual com a referencia, mas o resultado cego ficou editorialmente melhor; a referencia humana parece mais ruidosa e menos consolidada.
- video teste `Ad9885`: o subagente preservou o hook e reconstruiu bem o arco, mas reintroduziu o beat do `Grok` que no material real estava contaminado por tosse e direcao de set.

### Leitura nova

- as skills melhoraram bem a preservacao de detalhes concretos e de funis da casa
- o sistema continua acertando mais quando o problema e textual/editorial do que quando a decisao depende de qualidade real do audio
- `packed transcript` sozinho ainda pode superestimar a qualidade de um trecho

### Mudancas feitas apos a rodada 2

- nova skill `ad-house-funnels`
- reforco de regras para preservar funis recorrentes e detalhes invariantes
- reforco explicito de que transcript limpo nao implica audio limpo

## Round 3

Terceira rodada cega com:

1. `9119`
2. `8308`
3. `9298`
4. `8105`

### Resultado resumido

- `9119`: divergencia alta da referencia, mas por um bom motivo; a referencia foi auditada como `weak_reference` e a saida cega preservou melhor o funil `ranking -> Adapta Pass`.
- `8308`: bom desempenho em caso de rebuild agressivo; manteve precos, ferramentas, duracao de um ano e a condicao unica sem resumir a oferta.
- `9298`: manteve hook, mecanismo do PDF, prova cientifica e CTA limpo; ainda ha espaco para aproximar mais o wording final quando a referencia e forte.
- `8105`: excelente; preservou voz, segredo, escassez e o punch final `Vai, clica!`.

### Leitura nova

- o sistema melhorou visivelmente na preservacao de detalhes concretos da oferta
- o sistema melhorou visivelmente na preservacao de voz comercial quando o funil exige intimidade ou energia
- a nova auditoria de referencia ajuda a interpretar divergencia: baixa similaridade nem sempre significa pior resultado

### Mudancas feitas apos a rodada 3

- nova skill `ad-performance-voice`
- novo helper `anuncios_funnel_classifier.py`
- novo helper `anuncios_reference_audit.py`
- regra explicita de classificar pelo funil editorial dominante, nao so pela contagem bruta de termos

## Round 4

Quarta rodada cega com `strong references` para calibrar wording em funis diferentes:

1. `8078`
2. `8098`
3. `8104`
4. `8280`

### Resultado resumido

- `8098`: muito proximo da referencia forte; mecanismo do PDF, prova cientifica e CTA muito bem preservados
- `8280`: muito proximo da referencia forte; hook de sold out, anti-evento e qualificacao muito bem preservados
- `8078`: estruturalmente correto, mas ainda resumiu demais a metade da oferta
- `8104`: estruturalmente correto, mas ainda sofreu com corrupcao de entidade/canal e wording distante

### Leitura nova

- o sistema ja estava forte em estrutura e oferta concreta para alguns funis
- os gaps residuais mais importantes passaram a ser:
  - rotular melhor funis hibridos
  - reparar corrupcao obvia de ASR em nomes, marcas e canais

### Mudancas feitas apos a rodada 4

- novos funis no classificador e nas skills:
  - `anti_free_premium_status`
  - `authority_watch_report_back`
  - `summit_event`

## Round 5 and 6

Retestes focados nos casos residuais:

- `8078` com leitura explicita de `anti_free_premium_status`
- `8104` com leitura explicita de `authority_watch_report_back`
- `8104` novamente com regra nova de reparo de ASR de alta confianca

### Resultado resumido

- `8078`: melhorou de `0.445` para `0.638` de similaridade com a referencia forte
- `8104` ainda nao melhorou so com o novo funil
- `8104` melhorou drasticamente apos o reparo de entidade/ASR: `0.933`

### Mudancas feitas apos as rodadas 5 e 6

- regra explicita de reparo de entidade/ASR de alta confianca em `ad-editorial-decupagem`
- reforco de QC para detectar corrupcao de nomes/canais que reduz credibilidade mesmo quando a estrutura esta certa

## Round 7

Rodada de generalizacao em novos casos dos funis mais sensiveis:

1. `8079`
2. `8100`
3. `8116`
4. `8268`

### Resultado resumido

- `8079`: boa preservacao de pressao, degradacao da versao gratis e oferta concreta; similaridade `0.560`
- `8100`: boa preservacao do hook de arrependimento em tres meses e da oferta concreta; similaridade `0.493`
- `8268`: boa preservacao da autoridade Cariani, mecanismos concretos e exclusividade; similaridade `0.748`
- `8116`: similaridade muito baixa (`0.068`), mas o caso revelou que a referencia e uma `rewrite_reference`, nao wording-gold do bruto

### Leitura nova

- `anti_free_premium_status` generalizou melhor depois de virar funil explicito
- `authority_watch_report_back` tambem generalizou, mas precisa separar bem:
  - referencia forte e realmente pareada com o bruto
  - referencia boa, porem muito reescrita

### Mudancas feitas apos a rodada 7

- o auditor de referencia agora distingue `rewrite_reference`
- `8116` passou a ser tratado como exemplo de referencia boa, mas longe demais do bruto para servir de ouro literal

## Fine Calibration

Mineracao adicional apos as rodadas mostrou que `rewrite_reference` nao e uma coisa so.

Subtipos encontrados:

- `body_reframe`: `21`
- `full_rebuild`: `12`
- `hook_swap`: `1`

Leitura:

- o caso dominante e `body_reframe`: o par ainda e util, mas principalmente para estrutura e transicoes
- `full_rebuild` exige distancia ainda maior da referencia na hora de editar
- isso explica por que alguns casos pareciam falhas pelo score, quando na verdade o problema era usar a referencia errada como ouro de wording

## Reference Policy

Depois da mineracao, a calibracao virou policy explicita.

Novo helper:

- `helpers/anuncios_reference_policy.py`

Ele recomenda quanto peso dar a:

- wording
- estrutura

com base em:

- funil
- `reference_label`
- `rewrite_subtype`

Isso transforma a calibracao de excecoes em comportamento operacional reutilizavel, em vez de depender de julgamento ad hoc em cada sessao.

## Anchor Validation

So a policy abstrata ainda nao resolvia tudo.

No caso `8104`:

- `policy_only`: similaridade `0.213`
- `anchor_guided`: similaridade `0.652`

Leitura:

- para categorias como `follow_closely`, o agente funciona melhor quando recebe alguns anchors seguros da referencia, nao o `Final.txt` inteiro
- isso preserva a calibracao sem transformar a tool em substituto do trabalho editorial

Mudanca:

- novo helper `helpers/anuncios_reference_anchor_brief.py`

## Editor Brief Integration

Depois da validacao de policy + anchors, a calibracao foi integrada em um helper unico:

- `helpers/anuncios_reference_editor_brief.py`

Ele entrega para o agente:

- funil
- forca da referencia
- subtipo de rewrite
- peso de wording vs estrutura
- safe anchors
- checks de QC do caso

Leitura:

- isso reduz a chance de esquecer uma excecao importante no preparo do prompt
- mantem a decisao editorial no agente, mas entrega contexto calibrado de forma consistente

## Exception Mining and Funnel Confidence

Depois da integracao do editor brief, apareceu um proximo gargalo:

- algumas referencias fortes ainda pertenciam a funis com classificacao so `medium` ou `low`
- alguns anchors vazavam duplicados ou restos sem valor editorial
- havia uma familia medica consistente que ainda estava caindo em `unknown`

Mudancas:

- expansao do `summit_event` para sinais de `sold out`, cronologia e `anti-evento`
- nova familia `medico_nativo_ia`
- exposicao de `funnel_confidence`, `second_funnel`, `score_margin` e `hybrid_candidate`
- limpeza de anchors duplicados ou claramente ruidosos
- novo minerador `helpers/anuncios_exception_mining.py`

Estado posterior:

- `unknown` caiu para `1`
- `medico_nativo_ia` passou a ter `29` casos
- `summit_event` passou a ter `57` casos

Rodadas seguintes de calibracao tambem revelaram:

- uma familia `desafio_programa_ia`
- uma familia `trial_update_pack`
- uma auditoria de referencia mais rigida para finais curtos ou meta-ruidosos

Casos representativos:

- `8364`: migrou de `unknown` para `desafio_programa_ia`
- `8420`: migrou de leitura B2B frouxa para `trial_update_pack`
- `8282`: passou a ser tratado como `weak_reference`
- `8908`: passou a ser tratado como `review_reference`

## Residual Policy Calibration

Depois disso ainda sobrava um problema mais fino:

- muitos casos ainda ficavam `follow_closely` mesmo com `funnel_confidence` so `medium` ou `low`

Correcao:

- `follow_closely` agora degrada para `use_with_review` quando o funil esta baixo demais ou ainda dividido entre duas familias de forma material

Impacto:

- `follow_closely` ambiguo caiu de `143` para `22`

Rodada final dessa calibracao:

- percebeu-se que os `22` casos restantes nao eram ambiguos de verdade
- eles tinham um unico funil plausivel, sem `second_funnel`, mas continuavam `medium` por excesso de conservadorismo da heuristica

Correcao final:

- `top_score >= 2` sem `second_funnel` agora sobe para `high`

Impacto final:

- `follow_closely` ambiguo caiu de `22` para `0`

## Hybrid Matrix

Com a confianca residual resolvida, o principal ruido que restou foi qualitativo:

- `hybrid_candidate` sozinho dizia que havia sobreposicao, mas nao dizia se isso era benigno ou perigoso

Correcao:

- novo helper `helpers/anuncios_hybrid_matrix.py`
- novo artefato `Anuncios/hybrid_matrix.json`

Leitura:

- alguns pares sao recorrentes e relativamente normais, como `nine_premium_ais <-> whisper_secret`
- outros pares pedem mais cuidado editorial, como `authority_watch_report_back <-> cancel_chatgpt`

Resultado:

- o sistema agora nao so detecta hibrido
- ele tambem diferencia sobreposicao comum de sobreposicao arriscada

Leitura:

- agora a referencia forte continua valendo para estrutura
- mas o sistema evita imitar wording literalmente quando a leitura de funil ainda nao esta firme
- e, nos pares `dangerous_overlap`, a policy deixa de permitir `follow_closely` mesmo quando a referencia parece forte

Leitura:

- agora a calibracao de excecoes ficou mais explicita
- o minerador residual tambem passou a priorizar os casos em `high / medium / low` em vez de deixar todo hibrido no mesmo balde
- futuras rodadas podem mirar exatamente os `low` e `unknown`, em vez de recalibrar o corpus inteiro de novo

## Anchor Policy Validation

Validacao por categoria de policy:

- `8104` (`follow_closely`): `0.213 -> 0.652`
- `8095` (`use_with_review`): `0.688 -> 0.923`
- `8308` (`learn_structure_not_middle_wording`): `0.167 -> 0.419`
- `8116` (`funnel_only`): mantido sem anchors de wording

Leitura final:

- `follow_closely`: usar `safe anchors` deve ser padrao
- `use_with_review`: usar anchors leves tambem deve ser padrao
- `body_reframe`: usar anchors de edge e util
- `funnel_only`: nao usar anchors de wording
