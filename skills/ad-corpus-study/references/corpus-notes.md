# Corpus Notes

Baseado em `427` pares `Ad*_Bruto.txt -> Ad*_Final.txt`.

## O que o corpus mostra

- A maior parte dos finais nao e reescrita completa.
- Em `402/427` casos, o final e principalmente `cleanup editorial`.
- Em poucos casos, o bruto esta tao ruim que o final vira `reconstrucao agressiva`.
- Em poucos casos, o final fica maior do que o bruto porque o bruto-texto esta fraco, truncado ou mal transcrito.

## Regimes reais de edicao

### 1. Light to medium cleanup

Caso dominante.

Padrao:

- remove reset de fala
- remove direcao de cena
- remove repeticao literal
- remove frase abortada
- ajusta pontuacao
- preserva quase toda a copy

Exemplos:

- `8078`
- `8095`
- `8156`

### 2. Aggressive rebuild

Quando o bruto vem inflado por repeticao, tentativas multiplas, aquecimento ou bagunca de set.

Padrao:

- manter a espinha comercial
- escolher um hook funcional
- condensar blocos redundantes
- cortar varios takes internos da mesma ideia

Exemplos:

- `8308`
- `8311`
- `9298`
- `9304`

### 3. Expanded or rewritten final

Quando o bruto-texto parece incompleto, desorganizado ou subcapturado.

Padrao:

- o final nao segue o bruto literalmente
- ha sinal de copy mais bem formada do que a transcricao bruta
- nao assumir que o bruto e a verdade completa do anuncio

Exemplos:

- `8828`
- `8830`
- `8980`

## O que geralmente e cortado

- `volta`
- `mais`
- `aí`
- `pera aí`
- `opa`
- `gravando`
- conversa com equipe
- pergunta sobre wording
- correcoes de frase ao vivo
- duplicacao da mesma promessa
- CTA repetido duas vezes
- frase que quebra e recomeca limpa

## O que geralmente e preservado

- hook principal
- promessa comercial
- tese central
- prova ou justificativa
- condicao ou filtro
- CTA final

## Regra editorial mais importante

Nao confundir:

- `trecho mais limpo`

com

- `trecho mais correto comercialmente`

Em anuncio, o que manda e a copy inteira funcionar.

## Risco alto de erro

Se o transcript tiver:

- a mesma frase duas vezes com pequena variacao
- frase interrompida seguida de retomada limpa
- bloco de CTA em duas tomadas
- wording comentado com equipe

tratar como risco alto de duplicacao semantica no render.

## Regra de QC

QC bom de anuncio nao e so:

- pop de audio
- salto visual
- corte limpo

Tambem precisa validar:

- copy completa
- hook correto
- arco `Hook -> Lead -> Body -> Proof -> CTA`
- ausencia de eco semantico no ultimo terco

## Blind test learnings

Os primeiros blind tests com subagentes mostraram mais tres regras:

- nao abstrair demais a oferta; se o bruto traz detalhes concretos que vendem, manter esses detalhes
- nao normalizar demais a voz; fragmentos intencionais de performance podem ser parte do anuncio
- nem todo `Final.txt` do corpus deve ser tratado como ouro absoluto; alguns podem estar fracos, truncados ou corrompidos

### Detalhes concretos que merecem preservacao

- quantidade de IAs
- valores mensais
- nomes de ferramentas
- ranking ou posicao, se a copy depende disso
- condicao unica

## Familias recorrentes de funil

Algumas familias aparecem muitas vezes no corpus e merecem leitura propria:

- `nove IAs premium / stack de preco / gratis por um ano`
- `PDF gabarito / sobe o PDF / IA responde melhor`
- `cancelei o ChatGPT / bundle melhor do que uma IA so`
- `ranking das IAs / Adapta Pass em primeiro`
- `empresa nativa de IA / qualificador B2B`
- `segredo / sussurro / clica rapido`

Nessas familias, alguns detalhes nao sao enfeite. Sao o proprio motor de venda.

Leitura corpus-wide com o classificador atual:

- `nine_premium_ais`: `109`
- `anti_free_premium_status`: `63`
- `summit_event`: `57`
- `trial_update_pack`: `45`
- `pdf_gabarito`: `42`
- `medico_nativo_ia`: `29`
- `authority_watch_report_back`: `27`
- `empresa_nativa_ia`: `23`
- `desafio_programa_ia`: `11`
- `cancel_chatgpt`: `15`
- `ranking_adaptapass`: `4`
- `whisper_secret`: `3`

Estado atual de confianca do classificador:

- `high`: `272`
- `medium`: `115`
- `low`: `41`
- `unknown`: `1`

Importante:

- `whisper_secret` e um funil pequeno em volume, mas editorialmente muito sensivel
- alguns anuncios sao hibridos: a oferta pode ser `nine_premium_ais`, mas a moldura de venda dominante pode ser `whisper_secret`
- parte do corpus antes lido como `nine_premium_ais` na verdade funciona melhor como `anti_free_premium_status`
- parte do corpus antes lido como `cancel_chatgpt` na verdade funciona melhor como `authority_watch_report_back`
- surgiram novas familias consistentes no corpus: `medico_nativo_ia`, `desafio_programa_ia` e `trial_update_pack`
- agora resta apenas `1` caso `unknown`, que na pratica e um `Final.txt` corrompido de transcricao

### Familia nova: `medico_nativo_ia`

Padrao:

- autoridade medica ou especialista
- identidade `medico nativo de IA` ou `transplante de IA`
- mecanismos concretos de consultorio
- payoff de tempo, capacidade ou faturamento
- CTA para aula/video

Detalhes que costumam ser estruturais:

- `Paulo Muzy`
- `prontuario`
- `anamnese`
- `agenda`
- `paciente no WhatsApp`
- `10 a 15 horas por semana`, `ganhando o dobro`, `atendendo menos`

### Familia nova: `desafio_programa_ia`

Padrao:

- convite para desafio
- progressao por dia ou por tarefa
- payoff operacional concreto
- CTA para entrar no grupo, resgatar vaga ou comecar hoje

Detalhes estruturais comuns:

- `desafio de 5 dias`
- `uma IA por dia`
- `uma tarefa por dia`
- `grupo oficial do desafio`
- nichos profissionais, especialmente advogados

### Familia nova: `trial_update_pack`

Padrao:

- pacote novo, plataforma nova ou comemoracao
- `30 dias` de teste ou garantia
- prova por funcionalidades novas, presentes ou bonus
- CTA para assistir o video e ativar o teste

Detalhes estruturais comuns:

- `maior pacote de atualizacoes`
- `One26`
- `30 dias sem risco`
- `se nao gostar, devolve`
- `presentes extras`

### Confianca e hibridismo

O classificador agora nao entrega so `top_funnel`.

Ele tambem expõe:

- `funnel_confidence`
- `second_funnel`
- `score_margin`
- `hybrid_candidate`

Regra:

- `high`: usar a familia como guia forte
- `medium`: validar os detalhes contra a copy real
- `low` ou `unknown`: priorizar arco comercial bruto antes da leitura de familia
- `hybrid_candidate`: preservar os detalhes concretos que sustentam as duas leituras

## Matriz de hibridos

Novo helper:

- `helpers/anuncios_hybrid_matrix.py`

Novo artefato:

- `Anuncios/hybrid_matrix.json`

Ele separa pares de funil em tres classes:

- `benign_overlap`
- `review_overlap`
- `dangerous_overlap`

Leitura atual dos pares mais relevantes:

- `cancel_chatgpt <-> nine_premium_ais`: `review_overlap` (`54`)
- `nine_premium_ais <-> trial_update_pack`: `review_overlap` (`30`)
- `anti_free_premium_status <-> nine_premium_ais`: `review_overlap` (`28`)
- `authority_watch_report_back <-> cancel_chatgpt`: `dangerous_overlap` (`13`)
- `medico_nativo_ia <-> nine_premium_ais`: `dangerous_overlap` (`7`)
- `nine_premium_ais <-> whisper_secret`: `benign_overlap` (`5`)

Uso pratico:

- `benign_overlap`: a sobreposicao e esperada; manter os detalhes load-bearing do funil dominante costuma bastar
- `review_overlap`: usar wording com cautela e validar os beats concretos
- `dangerous_overlap`: evitar imitacao literal sem revisar bem o arco e os detalhes concretos

## Limites do modo transcript-only

Blind tests so com texto sao uteis, mas tem um limite claro:

- transcript limpo nao garante audio limpo
- um beat pode parecer correto no texto e ainda assim ter tosse, palma, crew ou retomada ruim no material

Para hook e CTA, se houver ruido de set perto do trecho, o agente precisa validar no material real antes de promover aquilo a melhor versao final.

## Confianca em `Final.txt`

Auditoria inicial do corpus com `helpers/anuncios_reference_audit.py`:

- `strong`: `329`
- `review_reference`: `61`
- `rewrite_reference`: `33`
- `weak_reference`: `6`

Regra pratica:

- `strong`: pode puxar bastante o entendimento editorial
- `review_reference`: usar como apoio, mas revisar duplicacao, truncamento e achatamento
- `rewrite_reference`: usar para aprender funil e movimentos estruturais, mas nao como ouro de wording
- `weak_reference`: o bruto e a logica comercial mandam mais do que a imitacao literal da referencia

Exemplo confirmado de `weak_reference`:

- `9119`

Exemplo confirmado de `rewrite_reference`:

- `8116`

Subtipos minerados em `rewrite_reference`:

- `body_reframe`: `21`
- `full_rebuild`: `12`
- `hook_swap`: `1`

Leitura pratica:

- `body_reframe` e o caso mais comum de reescrita
- nesses casos, o par ainda serve muito para aprender a espinha e os blocos de transicao
- `full_rebuild` pede mais distancia: aprender o funil, mas nao puxar wording

### Fragmentos de performance que podem ser validos

- `Oitavo!`
- `Free.`
- `Exato.`
- `Vai, clica!`

Se o fragmento aumenta urgencia, surpresa ou ritmo e nao e ruido de set, ele pode ser parte da copy final.

## Reparos de ASR de alta confianca

Outro erro residual importante apareceu nos blind tests:

- o funil podia estar correto, mas nomes e canais ficavam corrompidos pelo ASR

Regra:

- reparar entidade, marca, produto ou canal quando a intencao correta estiver obvia pelo contexto
- nao inventar fato novo
- usar o reparo so quando ele melhora a credibilidade da copy

Exemplos validos:

- `Cloud` -> `Claude`
- `Adaapta` -> `Adapta`
- `Antropic` -> `Anthropic`
- `Estragando Cariani` -> `Instagram do Cariani`

## Mineracao de rewrite references

Novo helper:

- `helpers/anuncios_rewrite_mining.py`
- `helpers/anuncios_reference_policy.py`

Ele separa `rewrite_reference` em subtipos operacionais:

- `body_reframe`
- `full_rebuild`
- `hook_swap`
- `cta_rewrite`

Exemplos:

- `8308` e `9298`: `body_reframe`
- `8116`: `full_rebuild`
- `8118`: `hook_swap`

Regra:

- `body_reframe`: usar a referencia para blocos e transicoes, nao para copiar wording do meio
- `full_rebuild`: usar so para aprender o funil e o tipo de promessa
- `hook_swap`: tratar o opener da referencia como alternativa editorial, nao como verdade literal do bruto

## Policy de peso da referencia

Novo helper:

- `helpers/anuncios_reference_policy.py`

Ele transforma:

- funil
- `reference_label`
- `rewrite_subtype`

em recomendacao operacional explicita:

- `wording_weight`
- `structure_weight`
- `policy`

Exemplos uteis:

- `8104`: `follow_closely`, wording alto, estrutura alta
- `9119`: `prefer_bruto`
- `8308`: `learn_structure_not_middle_wording`
- `8116`: `funnel_only`
- `8105`: `follow_closely`, com wording ainda mais alto por ser `whisper_secret`

Calibracao residual:

- `follow_closely` nao deve sobreviver automaticamente quando o funil ainda esta `medium` ou `low`
- se a referencia e forte, mas a leitura de funil ainda esta materialmente dividida, a policy agora degrada para `use_with_review`

Impacto corpus-wide:

- `follow_closely` caiu para `203`
- `use_with_review` subiu para `187`
- casos `follow_closely` com `funnel_confidence` nao-`high` cairam de `143` para `0`
- os `5` casos residuais de `dangerous_overlap` que ainda ficavam `follow_closely` tambem foram degradados para `use_with_review`

### Recalibracao de confianca sem segundo funil

Ultimo ajuste:

- quando um anuncio bate `top_score >= 2` em um unico funil e nao existe `second_funnel`, isso agora conta como `high`

Leitura:

- antes, varios casos corretos ficavam presos em `medium` por uma heuristica conservadora demais
- isso nao significava ambiguidade editorial real
- significava so que o funil tinha dois sinais fortes e nenhum competidor

Impacto:

- os `22` casos residuais de `follow_closely` ambiguo foram zerados
- a distribuicao de confianca foi para `272 high / 115 medium / 41 low / 1 unknown`

## Safe anchors da referencia

Novo helper:

- `helpers/anuncios_reference_anchor_brief.py`
- `helpers/anuncios_reference_editor_brief.py`

Leitura importante:

- `reference_policy` abstrata melhora a decisao
- mas, em casos `follow_closely`, ela sozinha ainda pode deixar o agente grudado demais no bruto
- passar alguns `safe anchors` da referencia corrige isso sem expor o `Final.txt` inteiro

Validacao direta:

- caso `8104`
- `policy_only`: similaridade `0.213`
- `anchor_guided`: similaridade `0.652`

Regra:

- `follow_closely`: passar anchors de abertura, alguns beats centrais e fechamento
- `use_with_review`: passar poucos anchors leves
- `body_reframe`: passar so edges se necessario
- `funnel_only`: nao passar anchors de wording

Acoplamento operacional:

- o fluxo agora nao depende mais de montar `funnel + audit + policy + anchors` manualmente
- `helpers/anuncios_reference_editor_brief.py` gera um bloco editorial unico, pronto para colar no prompt do agente
- quando o caso e `hybrid_candidate`, esse mesmo brief agora tambem explicita `hybrid_risk` e guidance por par (`benign_overlap`, `review_overlap`, `dangerous_overlap`)
- isso reduz erro de preparacao e mantem a tool como apoio, nao como substituta da decisao editorial
- `helpers/anuncios_exception_mining.py` agora minera os casos que ainda merecem calibracao manual com triagem mais explicita:
- `high`: `unknown_funnel`, `low_funnel_confidence`, `dangerous_hybrid_overlap`, anomalias de anchor
- `medium`: `review_hybrid_overlap`
- `low`: `benign_hybrid_overlap`

## Higiene de anchors

Outra calibracao fina feita:

- anchors agora removem duplicacao literal
- anchors agora filtram restos obvios como `Nada.`, `Boa.`, `Música.` e slugs de transcricao
- anchors agora preferem fechamento com CTA valido em vez do ultimo rabicho literal do texto

Casos corrigidos:

- `8102`: repeticao de anchor removida
- `9421`: anchors finais ruins como `Nada.` deixaram de vazar para o briefing
- `8364`: o fechamento agora privilegia o CTA do desafio, em vez de sobras performaticas finais

## Auditoria de referencia mais rigida

Nova calibracao:

- `Final.txt` muito curto agora cai mais facil para referencia fraca
- marcadores meta como `ta gravando`, `nao era pra voce estar gravando`, `Transcricao e Legendas`, `Pedro Negri` e afins agora pesam contra a confianca da referencia

Casos corrigidos:

- `8282`: deixou de parecer `rewrite_reference` util e passou a `weak_reference`
- `8908`: deixou de parecer `strong` e passou a `review_reference`

## Degradacao de policy por ambiguidade de funil

Nova regra:

- se a referencia seria `follow_closely`, mas o funil ainda esta `low`, a policy degrada
- se a referencia seria `follow_closely`, mas o funil esta `medium` e ainda materialmente dividido entre duas familias, a policy tambem degrada
- se a referencia seria `follow_closely`, mas o par hibrido ja esta classificado corpus-wide como `dangerous_overlap`, a policy tambem degrada mesmo com `funnel_confidence` alto

Intencao:

- continuar usando a referencia forte para estrutura
- parar de tratar wording como ouro quando a leitura de funil ainda esta ambigua

Casos representativos:

- `8118`: `authority_watch_report_back` vs `cancel_chatgpt`
- `8133`: `trial_update_pack` vs `nine_premium_ais`
- `8312`: `anti_free_premium_status` vs `nine_premium_ais`
- `8104`, `8539`, `8544`, `8987` e `9066`: deixaram de sobreviver como `follow_closely` porque o overlap do par ja se mostrou perigoso no corpus

Validacao:

- `8104` (`follow_closely`): `0.213 -> 0.652`
- `8095` (`use_with_review`): `0.688 -> 0.923`
- `8308` (`body_reframe`): `0.167 -> 0.419`

Leitura:

- `follow_closely`: anchors devem virar padrao
- `use_with_review`: anchors leves tambem ajudam bastante
- `body_reframe`: anchors de edge ajudam, mas menos; ainda sao uteis
- `funnel_only`: manter sem anchors de wording

## Round 3 learnings

Rodada cega focada em:

- `9119` para referencia fraca
- `8308` para rebuild pesado
- `9298` para PDF com detalhes concretos
- `8105` para voz e punch

Resultado:

- `8105` ficou praticamente colado na referencia e preservou `Vai, clica!`
- `8308` reconstruiu bem um bruto caotico sem perder precos, ferramentas, duracao e condicao
- `9298` preservou muito melhor os detalhes concretos do PDF, mas ainda pode divergir bastante na superficie textual mesmo quando a estrutura esta correta
- `9119` confirmou que referencia fraca nao deve puxar a decisao editorial; a saida cega ficou mais limpa e mais comercial que a referencia corrompida

## Round 4 and 5 learnings

Rodadas seguintes focaram em `strong references` para calibrar wording, nao so estrutura.

Casos bons:

- `8098` (`pdf_gabarito`) ficou muito proximo da referencia forte
- `8280` (`summit_event`) tambem ficou muito proximo da referencia forte
- `8078` melhorou bastante quando passou a ser tratado como `anti_free_premium_status` em vez de `nine_premium_ais` generico

Caso que expôs a falha mais fina:

- `8104` tinha o funil certo, mas ainda perdia credibilidade por corrupcao de entidade/canal no ASR

Correcao:

- adicionar regra explicita de reparo de ASR de alta confianca
- retestar `8104`

Resultado:

- `8104` saiu de similaridade `0.250`/`0.261` nas tentativas anteriores para `0.933` apos o reparo de entidades

## Round 7 learnings

Round 7 foi focada em testar generalizacao de:

- `anti_free_premium_status`
- `authority_watch_report_back`

Casos:

- `8079`
- `8100`
- `8116`
- `8268`

Leitura:

- `8079` e `8100` mostraram que o funil `anti_free_premium_status` esta generalizando de forma razoavel, com preservacao de pressao, prova de degradacao e oferta concreta
- `8268` mostrou boa generalizacao de `authority_watch_report_back`
- `8116` parecia uma falha pelo score baixo contra a referencia, mas na pratica expôs outra categoria: `rewrite_reference`

Resultado importante:

- quando a referencia e `rewrite_reference`, baixa similaridade nao prova erro do sistema
- nesses casos, o agente deve usar a referencia para aprender estrutura, nao para copiar wording
