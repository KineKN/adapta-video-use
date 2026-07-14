# Agent VM Setup for adapta-video-use

Este documento descreve o que enviar e instalar para rodar o `adapta-video-use` em uma VM, Hermes, Codex, Claude Code ou outro agente com acesso ao shell.

## Arquivos Do Repo

Clone o repositório completo:

```bash
git clone https://github.com/KineKN/adapta-video-use.git
cd adapta-video-use
```

Arquivos e pastas importantes:

- `SKILL.md`
- `agent/Main.md`
- `agent/persona/SOUL.md`
- `agent/persona/IDENTITY.md`
- `agent/persona/USER.md`
- `install.md`
- `README.md`
- `pyproject.toml`
- `.env.example`
- `helpers/`
- `skills/`
- `tests/` se o agente também for validar/desenvolver

O diretório `helpers/` contém os scripts executáveis do pipeline:

- `transcribe.py`
- `transcribe_batch.py`
- `pack_transcripts.py`
- `timeline_view.py`
- `render.py`
- `grade.py`
- `remove_silence.py`
- `edl_boundary_audit.py`
- `export_premiere_xml.py`
- scripts `anuncios_*` para análise de corpus/anúncios

O diretório `skills/` contém instruções especializadas. Para anúncios, a memória consolidada fica em:

```text
skills/ad-corpus-study/references/
```

Para editar anúncios, leia primeiro:

```text
skills/ad-corpus-study/references/golden-editing-standard.md
```

Esse arquivo consolida o padrão de qualidade, as regras de QC e os aprendizados dos benchmarks de edição.

## O Que Não Faz Parte Do Repo

Não versionar nem enviar:

- `.env`
- `.venv/`
- `.venv_ads/`
- `node_modules/`
- `Anuncios/`
- `blind_tests/`
- `teste/`
- `edit/`
- `static/`
- `poster.html`
- renders, previews, vídeos e artefatos temporários
- chaves, tokens, `.pem`, `.key`

`Anuncios/` e `blind_tests/` são datasets/artefatos locais. A memória útil deles já foi consolidada nos arquivos versionados em `skills/ad-corpus-study/references/`.

## Software Obrigatório

### Python

Use Python `3.11` se puder escolher.

O projeto declara:

```text
requires-python >=3.10
```

Python `3.10`, `3.11` ou `3.12` pode funcionar. Em Alpine Linux/arm64, algumas libs científicas podem não ter wheels prontos; nesse caso Debian/Ubuntu costuma ser mais simples.

### ffmpeg

Obrigatório:

- `ffmpeg`
- `ffprobe`

Sem isso o projeto não consegue inspecionar mídia, extrair áudio, gerar timeline views, renderizar nem exportar corretamente.

### Dependências Python

Na raiz do projeto:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Ou, se `uv` estiver disponível:

```bash
uv sync
```

Dependências base do `pyproject.toml`:

- `requests`
- `librosa`
- `matplotlib`
- `pillow`
- `numpy`

Se `matplotlib`/`librosa` não instalarem em Alpine/arm64, o pipeline principal ainda pode funcionar sem `timeline_view.py`, mas a inspeção visual fica limitada. Preferir Debian/Ubuntu quando precisar do stack completo.

### ElevenLabs API Key

Necessária apenas para transcrever com `helpers/transcribe.py`.

Criar `.env` na raiz:

```bash
ELEVENLABS_API_KEY=coloque_a_chave_aqui
```

Não commitar `.env`.

Se o agente já receber transcrições prontas, a chave não é obrigatória.

## Software Opcional

### Node.js

Necessário apenas para HyperFrames ou Remotion.

Recomendado:

- Node.js `22 LTS` ou mais novo;
- npm.

Node `20` é suficiente para o pipeline base, mas pode não ser suficiente para HyperFrames.

### yt-dlp

Opcional. Instale só se for baixar vídeos de URLs.

### Manim

Opcional. Use apenas para animações matemáticas/técnicas.

```bash
pip install -e ".[animations]"
```

### WhisperX / NLP Local

Opcional e pesado. Use apenas para fallback ASR local, estudo de corpus ou lote offline.

Requer:

- GPU NVIDIA com CUDA para bom desempenho;
- `torch` compatível com o driver/CUDA;
- `whisperx`;
- `transformers`;
- `sentence-transformers`;
- `rapidfuzz`;
- `pandas`;
- `scikit-learn`;
- `spacy`.

Não envie `.venv_ads`; recrie o ambiente na máquina alvo se precisar.

## Instalação Em Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip ffmpeg git curl

git clone https://github.com/KineKN/adapta-video-use.git
cd adapta-video-use

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Node 22, se precisar:

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v
npm -v
```

## Instalação Em macOS

```bash
brew install python@3.11 ffmpeg

git clone https://github.com/KineKN/adapta-video-use.git
cd adapta-video-use

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Node 22, se precisar:

```bash
brew install node@22
```

## Verificação Mínima

```bash
source .venv/bin/activate
python helpers/transcribe.py --help
python helpers/transcribe_batch.py --help
python helpers/pack_transcripts.py --help
python helpers/render.py --help
python helpers/grade.py --help
python helpers/remove_silence.py --help
python helpers/edl_boundary_audit.py --help
python helpers/export_premiere_xml.py --help
ffprobe -version
ffmpeg -version
```

Teste opcional do `timeline_view.py`:

```bash
python helpers/timeline_view.py --help
```

## Premiere XML

Para gerar XML importável no Premiere, não precisa instalar Adobe Premiere na VM.

```bash
python helpers/export_premiere_xml.py edit/edl.json \
  -o edit/premiere_export.xml \
  --sequence-name MinhaSequencia
```

Importe depois no Premiere via `File > Import`.

Premiere Pro não existe para Linux. Linux pode gerar o XML, mas não abrir Premiere localmente.
