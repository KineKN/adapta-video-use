# USER

## Contexto do usuário

Este arquivo deve ser ajustado para cada pessoa ou equipe que usar o assistente. Ele não define a identidade do projeto; apenas registra preferências persistentes do operador.

## Preferências padrão sugeridas

- Idioma de interação: português, a menos que o usuário peça outro idioma.
- Comunicação: objetiva, técnica e com foco em entregáveis.
- Preferir caminhos de arquivos absolutos ao entregar artefatos locais.
- Quando a tarefa envolver código ou edição local, executar no workspace em vez de apenas sugerir passos.
- Quando entregar XML, informar o caminho final e o tipo de sequência gerada.

## Contexto operacional

- O projeto deve ser clonado em um caminho estável da máquina do agente.
- Outputs de cada vídeo devem ficar na pasta `edit/` ao lado das mídias ou em subpastas claras dentro dela.
- `.env` no root do projeto pode conter `ELEVENLABS_API_KEY`.
- Ambientes locais opcionais, como WhisperX/NLP, devem ser recriados na máquina alvo e não versionados.

## O que perguntar quando faltar contexto

- Qual é o objetivo do vídeo?
- Qual formato de entrega importa: MP4 final, preview, XML para Premiere, legendas, overlays ou todos?
- Qual proporção/resolução alvo?
- O usuário quer estratégia antes da edição ou execução direta?
- Há momentos obrigatórios para preservar ou cortar?
