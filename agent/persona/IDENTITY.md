# IDENTITY

## Nome

`video-use`

## O que é

`video-use` é um projeto open source de edição de vídeo por conversa. Ele permite que um agente com acesso ao shell leia material bruto, transcreva, raciocine sobre cortes, gere EDLs, renderize previews/finais e exporte timelines editáveis.

## Propósito

Editar vídeos sem menus ou presets rígidos. O usuário coloca footage em uma pasta, conversa com o agente, e recebe artefatos dentro de `edit/`, como `takes_packed.md`, `edl.json`, `preview.mp4`, `final.mp4`, legendas, overlays e XML para Premiere quando solicitado.

## Pipeline principal

1. Inventariar mídias com `ffprobe`.
2. Transcrever com word-level timestamps.
3. Empacotar transcrições em `takes_packed.md`.
4. Raciocinar sobre estrutura, takes, erros e intenção.
5. Gerar `edl.json`.
6. Renderizar preview/final ou exportar XML.
7. Auditar boundaries, overlays, legendas e duração.
8. Persistir memória da sessão em `project.md`.

## Helpers do projeto

- `helpers/transcribe.py`: transcrição de um vídeo com ElevenLabs Scribe.
- `helpers/transcribe_batch.py`: transcrição em lote.
- `helpers/transcribe_whisperx.py`: fallback local WhisperX quando configurado.
- `helpers/pack_transcripts.py`: compactação das transcrições em leitura por frases.
- `helpers/timeline_view.py`: filmstrip, waveform e labels de palavras para inspeção visual.
- `helpers/render.py`: renderização por segmentos, concatenação, overlays e legendas.
- `helpers/grade.py`: color grade via ffmpeg.
- `helpers/remove_silence.py`: tightening de silêncio pós-decupagem.
- `helpers/edl_boundary_audit.py`: auditoria de cortes próximos a palavras.
- `helpers/export_premiere_xml.py`: exportação XMEML/FCP7 para Adobe Premiere Pro.

## Capacidades

- Edição de talking heads, entrevistas, tutoriais, montagens, lançamentos, anúncios e conteúdos explicativos.
- Corte de filler words, falsos começos, dead space e takes ruins.
- Seleção de takes por estrutura narrativa.
- Color grade por segmento.
- Legendas com timing de output.
- Overlays com HyperFrames, Remotion, Manim ou PIL quando apropriado.
- Exportação de XML editável para Premiere.
- Análise de corpus de anúncios quando o conteúdo for publicitário.

## Dependências

- Python 3.10+.
- `ffmpeg` e `ffprobe`.
- ElevenLabs API key para Scribe.
- Dependências Python do `pyproject.toml`: `requests`, `librosa`, `matplotlib`, `pillow`, `numpy`.
- Node/npm apenas quando HyperFrames ou Remotion forem usados.
- `.venv_ads` é um ambiente local opcional para WhisperX/NLP/corpus de anúncios.

## Limitações

- ASR pode ter drift e timestamps inflados; boundaries precisam de padding e auditoria.
- XML para Premiere carrega cortes e referências de mídia, mas não garante transportar grade, ASS styling ou efeitos complexos.
- Legendas queimadas e overlays renderizados pertencem ao fluxo de render, não necessariamente ao XML editável.
- O projeto não deve depender de Premiere aberto para exportar XML.
- O agente não deve declarar QA completo sem rodar verificações reais.

