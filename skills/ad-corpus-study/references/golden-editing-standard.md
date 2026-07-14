# Padrao De Edicao De Anuncios

Este documento contem o padrao de edicao de anuncios para `adapta-video-use`.

Use apenas o repositorio, o video atual, o transcript gerado para esse video e as ferramentas do projeto. Todo aprendizado necessario esta consolidado nas regras abaixo.

## Objetivo

O objetivo nao e "encurtar o video".

O objetivo e entregar um anuncio que pareca uma unica peca comercial intencional:

- copy completa;
- hook preservado;
- repeticoes removidas;
- ritmo firme;
- silencio morto removido;
- respiracoes e pre-fala removidas quando nao forem performance;
- CTA final completo;
- nenhum corte quebrando fala.

## Conceitos

`Bruto` significa material original antes da edicao: video com erros, retomadas, pausas, repeticoes, conversa de set e tentativas alternativas.

`Final` significa a copy limpa que deveria sobrar depois da decupagem: uma sequencia coerente de anuncio.

Esses termos descrevem o tipo de transformacao editorial. Nao procurar arquivos chamados `Bruto` ou `Final` para aplicar este padrao.

`EDL` e a lista de cortes: source, start, end, beat, quote e reason.

`Decupagem` e escolher o que pertence ao anuncio.

`Remove silence` e apertar o ritmo depois da decupagem.

## Regra Central

Decupagem vem antes de silencio.

Primeiro remover tomada errada, reset, repeticao e trecho fora da copy. Depois aplicar uma passada de ritmo para cortar silencio morto e bordas ruins.

Nunca usar remocao de silencio para decidir qual frase pertence ao anuncio.

## Fluxo Obrigatorio

1. Inventariar o video com `ffprobe`.
2. Transcrever com timestamps de palavra ou carregar transcript cacheado.
3. Ler o transcript como anuncio, nao como texto generico.
4. Mapear `Hook -> Lead -> Body -> Proof -> CTA`.
5. Selecionar a melhor tomada continua de cada bloco.
6. Remover set noise, resets, falsos comecos e repeticoes.
7. Criar o primeiro EDL editorial.
8. Rodar `helpers/edl_boundary_audit.py`.
9. Aplicar `helpers/remove_silence.py` sobre o EDL ja decupado se o usuario pediu ritmo dinamico ou anuncio direto.
10. Rodar auditoria de boundary de novo.
11. Exportar XML ou renderizar a partir do EDL final.
12. Conferir copy, boundary e ritmo antes de entregar.

Se o resultado sair da primeira passada sem nenhuma revisao de ritmo e boundary, trate como rascunho, nao como final.

## Estrutura Comercial

Antes de aprovar, escreva mentalmente:

```text
HOOK: o que faz a pessoa parar?
LEAD: que problema, tese ou promessa abre o anuncio?
BODY: qual mecanismo ou oferta sustenta a promessa?
PROOF: por que acreditar agora?
CTA: qual acao final o usuario deve tomar?
```

Se uma dessas partes sumiu, a edicao esta incompleta mesmo que os cortes estejam tecnicamente limpos.

## Preservar Agressivamente

Preserve:

- promessa comercial;
- tensao ou problema;
- mecanismo concreto;
- prova ou autoridade;
- condicao unica da oferta;
- numeros, precos, datas, quantidades e nomes;
- CTA completo;
- performance que aumenta urgencia, surpresa, intimidade ou ritmo.

Nao trocar o hook verdadeiro por uma linha mais limpa se isso enfraquece a promessa.

Nao transformar detalhe concreto em resumo generico.

## Cortar Agressivamente

Corte:

- direcao de set;
- conversa com equipe;
- comentario sobre wording;
- aquecimento de fala;
- frase abortada;
- falsa partida;
- reset seguido de retomada limpa;
- repeticao literal;
- repeticao semantica;
- prova duplicada;
- CTA duplicado sem intencao;
- silencio morto;
- respiracao pre-fala que nao vende;
- vazamento de frase abandonada depois de uma frase mantida.

Palavras como `volta`, `mais`, `pera ai`, `opa`, `ta gravando` e similares normalmente sao reset quando aparecem fora da copy.

## Familias De Funil

Use estas familias como mapa de preservacao. Elas nao sao categorias rigidas. O anuncio atual manda.

### Nine Premium AIs / Stack De Preco

Padrao:

`ancora de preco -> ferramentas premium -> custo empilhado -> condicao surpreendente -> CTA`

Preserve:

- nomes das ferramentas;
- quantidade, como `9` ou `nove`;
- comparacao de custo mensal;
- `premium`, `gratis`, `por um ano` quando forem a promessa;
- a condicao unica que libera a oferta.

Erro comum: deixar so "varias IAs" e apagar o stack que faz a oferta parecer valiosa.

### PDF Gabarito

Padrao:

`curiosidade ou autoridade -> anexar PDF -> IA responde melhor -> prova cientifica -> CTA`

Preserve:

- `PDF` como objeto especifico;
- mecanismo de anexar/subir PDF;
- alivio de nao precisar ler;
- prova cientifica quando existir;
- caminho de aquisicao do PDF.

Erro comum: trocar `PDF gabarito` por "um documento" e matar o mecanismo.

### Cancel ChatGPT / Bundle Melhor

Padrao:

`cancelei ChatGPT -> uma IA so nao basta -> varios modelos premium -> comparacao por tarefa -> teste/garantia -> CTA`

Preserve:

- hook de cancelamento;
- modelos nomeados;
- razao de cada modelo;
- comparacao de preco separado vs bundle;
- janela de teste, garantia ou aumento de preco.

Erro comum: remover os usos por modelo e deixar uma promessa generica.

### Ranking / Adapta Pass Numero Um

Padrao:

`ranking externo -> julgamento rapido das ferramentas -> Adapta Pass absorve vencedores -> utilidade de negocio -> primeiro lugar`

Preserve:

- existencia do ranking;
- alguns exemplos concretos;
- porque Adapta Pass nao e so uma IA;
- conclusao de primeiro lugar quando for payoff.

Erro comum: cortar exemplos demais e fazer o ranking perder sentido.

### Empresa Nativa De IA

Padrao:

`qualificador de empresa -> autoridade -> transformacao B2B -> programa especial -> CTA`

Preserve:

- limite ou qualificador, como faturamento ou tamanho;
- expressao `empresa nativa de IA`;
- autoridade e escala;
- posicionamento de programa especial.

Erro comum: transformar em produtividade generica.

### Whisper / Secret / Fast CTA

Padrao:

`segredo intimista -> promessa surpreendente -> condicao unica -> escassez -> CTA urgente`

Preserve:

- tom de segredo;
- sussurro ou intimidade;
- promessa exata;
- condicao unica;
- imperativos curtos como `Vai, clica!` quando forem performance.

Erro comum: normalizar o sussurro em fala plana.

### Anti-Free vs Premium / Status Threat

Padrao:

`ameaca de status -> ferramenta gratis humilha -> prova de degradacao -> premium necessario -> oferta de resgate -> CTA`

Preserve:

- opener agressivo;
- prova concreta de degradacao;
- ponte entre problema e oferta;
- oferta de resgate;
- gate ou condicao.

Erro comum: manter a dor e apagar o resgate.

### Authority Watch And Report Back

Padrao:

`confissao pessoal -> autoridade conhecida -> tecnica ou mecanismo incomum -> pedido de validacao -> acesso escondido`

Preserve:

- confissao ou pedido de ajuda;
- autoridade nomeada;
- mecanismos concretos;
- loop "assiste e me diz";
- virada de acesso escondido.

Erro comum: virar uma recomendacao generica.

### Summit Event / Sold-Out

Padrao:

`escassez -> prova de edicao esgotada -> edicao maior -> anti-evento -> qualificacao -> CTA`

Preserve:

- sold out;
- datas e cronologia;
- escala;
- diferenca contra evento comum;
- filtro de quem entra;
- caminho para garantir vaga.

Erro comum: transformar em hype generico de evento.

### Medico Nativo De IA

Padrao:

`autoridade medica -> identidade nativa de IA -> mecanismo de consultorio -> payoff de tempo/receita -> CTA`

Preserve:

- especialidade;
- identidade `medico nativo de IA` ou `transplante de IA`;
- mecanismos como prontuario, anamnese, agenda, WhatsApp;
- payoff de tempo, capacidade ou faturamento;
- autoridade nomeada quando existir.

Erro comum: apagar o mecanismo clinico e deixar so "usar IA".

### Desafio Programa De IA

Padrao:

`convite para desafio -> progresso por dia/tarefa -> payoff operacional -> urgencia -> CTA`

Preserve:

- mecanica de desafio;
- publico alvo;
- progressao por dia ou tarefa;
- grupo, botao, convite ou data;
- resultado operacional concreto.

Erro comum: transformar desafio em aula generica.

### Trial Update Pack

Padrao:

`lancamento ou update -> maior pacote/plataforma nova -> teste sem risco -> bonus/prova -> CTA`

Preserve:

- 30 dias ou teste sem risco;
- novidade do pacote;
- ferramentas, features, bonus ou presentes;
- caminho de devolucao/garantia quando existir.

Erro comum: apagar a mecanica de teste e deixar so valor amplo.

## Conhecimento Consolidado

O aprendizado consolidado mostra tres regimes de edicao:

- `light_to_medium_cleanup`: caso dominante; preserva quase toda copy e limpa ruido.
- `aggressive_rebuild`: usado quando o material tem muitas tentativas e repeticoes.
- `expanded_or_rewritten`: raro; usado quando a fala capturada esta incompleta ou muito fraca.

Aplicacao pratica:

- por padrao, preserve a copy e limpe o ruido;
- so faca rebuild agressivo quando o material realmente estiver redundante ou desorganizado;
- nao assuma que o trecho mais curto e o melhor;
- nao assuma que toda referencia textual fornecida pelo usuario e ouro absoluto;
- se o usuario fornecer uma referencia final, use como apoio, mas ainda valide hook, body, proof e CTA.

Se nenhuma referencia textual for fornecida, nao procure arquivos externos. Trabalhe apenas com o video, o transcript e este padrao.

## Voz E Performance

Nao neutralizar demais.

Fragmentos curtos podem ser parte da venda:

- `Oitavo!`;
- `Free.`;
- `Exato.`;
- `Vai, clica!`.

Preserve quando o fragmento cria punch, urgencia, surpresa, intimidade ou ritmo.

Corte quando for set noise, erro, aquecimento ou sobra de tomada.

## Repeticoes

Tipos de repeticao:

- literal: a mesma frase aparece de novo;
- semantica: a mesma ideia aparece com wording diferente;
- estrutural: duas provas ou dois CTAs ocupam o mesmo papel;
- reset: frase quebra e volta limpa depois.

Regra:

- manter uma versao;
- escolher a melhor performance que preserva a copy;
- cortar a versao abortada inteira;
- nao concatenar meio pensamento com a retomada limpa.

## Reparos De ASR

Corrija ASR obvio quando a intencao for clara e comercialmente importante.

Exemplos:

- `Cloud` -> `Claude`;
- `Adaapta` -> `Adapta`;
- `Antropic` -> `Anthropic`;
- nome de canal, pessoa, produto ou marca claramente corrompido.

Nao inventar fato novo.

## Silencio

Silencio nao tem valor fixo universal.

Cada audio deve ser analisado pelo proprio material. O threshold correto depende do ruido, microfone, sala, voz e compressao.

Regra:

- nao usar dB universal como decisao editorial;
- nao cortar silencio antes da decupagem;
- nao aceitar microcorte que remove 1 a 4 frames e nao muda ritmo;
- nao cortar fala real para ganhar poucos frames;
- nao deixar pausa morta perceptivel entre frases em anuncio direto;
- nao deixar respiracao pre-fala quando ela nao vende.

Comandos base:

```bash
python helpers/remove_silence.py edit/edl.json --audio-tighten --mode tight --out edit/edl_tight.json
python helpers/edl_boundary_audit.py edit/edl_tight.json
```

Para comportamento mais proximo de um silence remover baseado em waveform:

```bash
python helpers/remove_silence.py edit/edl.json --audio-tighten --mode tight --ffmpeg-silence-only --out edit/edl_ffmpeg_tight.json
python helpers/edl_boundary_audit.py edit/edl_ffmpeg_tight.json
```

Se ainda houver respiracao nas bordas:

```bash
python helpers/remove_silence.py edit/edl.json --audio-tighten --mode tight --ffmpeg-silence-only --breath-edge-trim --out edit/edl_breath_tight.json
python helpers/edl_boundary_audit.py edit/edl_breath_tight.json
```

Parametros manuais existem para debug e reproducao, nao para virar default global.

## Respiracao

Respiracao nao e necessariamente silencio.

Ela pode aparecer na waveform e ainda assim quebrar o ritmo.

Tratar assim:

- cortar pre-fala antes da primeira palavra real;
- aparar bordas infladas por ASR;
- revisar respiracoes entre duas falas;
- preservar respiracao se for suspense, whisper, segredo ou performance intencional.

## Boundary Rules

Erros proibidos:

- cortar o final de palavra;
- comer o inicio de palavra;
- deixar silaba incompleta antes do corte;
- vazar inicio de frase abandonada;
- cortar fala real por poucos frames;
- quebrar o CTA;
- cortar palavra final como `grupo`, `embaixo`, `aqui`, `agora`.

Se uma frase mantida termina e outra frase abortada comeca logo depois, nao termine no ataque da frase abortada. Termine antes do ataque.

Se `edl_boundary_audit.py` reportar `inside_word`, trate como blocker.

Se reportar `too_close_to_*`, revise manualmente.

## Iteracao Esperada

Um bom resultado normalmente tem pelo menos duas versoes:

- `edl_editorial`: copy correta, repeticoes removidas;
- `edl_tight`: ritmo apertado, silencio morto removido.

Se houver corte de fala, descarte a versao agressiva e volte para word-safe.

Se sobrar silencio, rode nova passada de ritmo sem mexer na copy.

Se sobrar respiracao, trate como problema de borda, nao como repeticao.

## Benchmark De Qualidade

Os melhores resultados observados tinham:

- mais cortes uteis;
- duracao media menor por clip;
- ausencia de microcortes;
- zero corte dentro de fala;
- iteracao apos feedback;
- QC de boundary antes da entrega.

Referencias numericas observadas:

```text
Benchmark A:
- 29 clips principais
- duracao media por clip perto de 2.5s
- 28 gaps de fonte removidos
- nenhum microcorte abaixo de aproximadamente 120ms
- varias iteracoes ate chegar no resultado bom

Benchmark B:
- 37 clips principais
- duracao media por clip perto de 2.5s
- 36 gaps de fonte removidos
- nenhum microcorte abaixo de aproximadamente 120ms
- uma versao agressiva foi descartada por cortar fala
- a versao final priorizou word-safe e no-microcuts
```

Essas metricas nao sao metas universais. Elas ensinam o padrao:

- remover bastante quando existem pausas reais;
- nao gerar corte inutil;
- descartar qualquer versao que corta fala;
- iterar ate o rhythm pass ser perceptivelmente melhor.

Resultados mais fracos geralmente tinham:

- poucos clips;
- clips longos demais;
- menos gaps removidos;
- uma unica passada;
- pouca auditoria de boundary;
- silencio residual claro.

## WhisperX E NLP

WhisperX e NLP sao recursos opcionais. Use apenas quando estiverem disponiveis e funcionando no ambiente atual. VPS, container Linux, Alpine, CPU-only ou maquinas sem CUDA podem nao suportar esse stack com desempenho suficiente.

Nao trate WhisperX, NLP ou MPNet como requisito obrigatorio para editar. Se nao estiverem disponiveis, continue com transcript word-level, ffmpeg, EDL, auditoria de boundary e decisao editorial.

Use WhisperX quando:

- ElevenLabs nao estiver disponivel;
- for preciso fallback local;
- timestamps do transcript principal estiverem ruins;
- houver lote grande e GPU disponivel.

Use NLP/MPNet quando:

- repeticao semantica estiver dificil de detectar por leitura;
- o transcript for longo;
- houver lote de muitos videos.

Mesmo quando WhisperX/NLP existem, a diferenca de qualidade vem principalmente de:

- timestamps de palavra;
- audio profiling por video;
- boundary QC;
- iteracao;
- decisao editorial correta.

## XML Para Premiere

XML importavel nao significa edicao boa.

Antes de entregar XML:

- exportar a partir do EDL final;
- conferir duracao;
- garantir que o XML nao reintroduziu pre-roll antes da fala;
- garantir que video e audio estao sincronizados;
- se houver headline/overlay, garantir track separada e duracao correta.

## QC Obrigatorio

Checklist:

- hook existe;
- lead existe;
- body existe;
- proof existe quando a copy depende dele;
- CTA existe e esta completo;
- oferta concreta sobreviveu;
- nao ha repeticao semantica;
- nao ha CTA duplicado;
- nao ha palavra cortada;
- nao ha silaba vazada;
- nao ha microcorte inutil;
- nao ha silencio morto perceptivel;
- respiracoes ruins foram removidas quando possivel;
- o EDL exportado e a versao aprovada.

Rodar:

```bash
python helpers/edl_boundary_audit.py edit/edl_final.json
```

## Uso Em Ambiente Novo

Em um ambiente novo:

- ler este documento antes de editar anuncios;
- nao procurar material externo ao repo e ao video atual;
- nao depender de exemplos que nao estao no repo;
- nao entregar primeira passada sem QC;
- criar EDLs versionados quando iterar;
- medir clips, duracao e gaps removidos;
- explicar qual versao foi descartada quando houver erro;
- priorizar word-safe quando houver risco de fala cortada;
- aplicar rhythm pass sem alterar a copy;
- tratar respiracao como problema de borda/performance.

## Sinais De Falha

Falha editorial:

- hook sumiu;
- lead virou hook indevidamente;
- body ficou sem mecanismo;
- CTA duplicou;
- CTA foi cortado;
- detalhe concreto virou resumo generico.

Falha de ritmo:

- ainda ha pausas mortas claras;
- ha respiracao pre-fala constante;
- parece decupado, mas nao apertado;
- clips longos demais por falta de rhythm pass.

Falha de boundary:

- palavra final cortada;
- inicio de palavra comido;
- silaba incompleta;
- corte de poucos frames em fala;
- corte onde nao havia silencio real.

## Criterio De Aprovacao

Um anuncio aprovado passa em tres niveis:

1. Semantico: a copy vende e esta completa.
2. Tecnico: cortes, audio e XML nao quebram.
3. Ritmico: o video ficou perceptivelmente mais dinamico sem ficar picotado.

Se qualquer nivel falhar, a entrega ainda nao esta pronta.
