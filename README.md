# adapta-video-use

Projeto para agentes da equipe editarem vídeos por conversa com um fluxo padronizado de transcrição, EDL, renderização, auditoria e exportação XML.

Inclui:

- persona e prompts para agentes em `agent/`;
- guia geral de setup em `AGENT_SETUP.md`;
- skills de edição de anúncios e memória editorial consolidada;
- exportação XML para Adobe Premiere Pro;
- ferramentas de silêncio, auditoria de borda e decupagem com EDL;
- instruções para configurar o ambiente em agentes como Codex, Hermes e Claude Code.

## Para Que Serve

O agente usa este repo para:

- transcrever vídeos com timestamps de palavra;
- empacotar transcrições em `takes_packed.md`;
- montar um `edl.json` com decisões de corte;
- remover erros, falsos começos, repetições e pausas ruins;
- renderizar preview/final quando necessário;
- exportar XML editável para Premiere;
- auditar boundaries para evitar cortes dentro de fala;
- seguir memória editorial de anúncios sem precisar baixar o corpus bruto.

## Estrutura Do Repo

```text
.
├── agent/
│   ├── Main.md
│   └── persona/
│       ├── SOUL.md
│       ├── IDENTITY.md
│       └── USER.md
├── helpers/
├── skills/
│   ├── ad-corpus-study/
│   │   └── references/
│   ├── ad-copy-structure/
│   ├── ad-editorial-decupagem/
│   ├── ad-house-funnels/
│   ├── ad-local-asr-nlp/
│   ├── ad-performance-voice/
│   ├── ad-semantic-qc/
│   ├── manim-video/
│   ├── premiere-xml-export/
│   └── remove-silence-post/
├── tests/
├── AGENT_SETUP.md
├── SKILL.md
├── install.md
└── pyproject.toml
```

## Arquivos Principais

- `SKILL.md`: instruções operacionais centrais do video-use.
- `AGENT_SETUP.md`: guia para instalar em uma VM, Hermes, Codex ou outro agente.
- `agent/Main.md`: nome + system prompt para cadastro em agente.
- `agent/persona/SOUL.md`: persona e comportamento base.
- `agent/persona/IDENTITY.md`: capacidades e limites factuais do agente.
- `agent/persona/USER.md`: template de contexto do usuário/equipe.
- `helpers/`: scripts reais de transcrição, render, EDL, XML e auditoria.
- `skills/`: instruções especializadas para anúncios, Premiere XML, silêncio e animações.
- `skills/ad-corpus-study/references/`: memória editorial consolidada do corpus de anúncios, incluindo o padrão de referência `golden-editing-standard.md`.

## Instalação Rápida

```bash
git clone https://github.com/KineKN/adapta-video-use.git
cd adapta-video-use

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Instale também `ffmpeg` e `ffprobe`.

Para transcrição com ElevenLabs, crie `.env` na raiz:

```bash
ELEVENLABS_API_KEY=sua_chave
```

Leia `AGENT_SETUP.md` para setup completo por ambiente.

## Dependências

Obrigatórias:

- Python `>=3.10` (`3.11` recomendado; `3.12` funciona se as libs instalarem no sistema);
- `ffmpeg`;
- `ffprobe`;
- dependências do `pyproject.toml`.

Opcionais:

- Node.js `22+` para HyperFrames/Remotion;
- `yt-dlp` para baixar vídeos por URL;
- Manim para animações matemáticas;
- WhisperX/NLP local para fallback ASR e análise de corpus.

## Uso Por Agente

Fluxo base:

1. Ler `SKILL.md`.
2. Ler skills específicas conforme a tarefa.
3. Inventariar mídia com `ffprobe`.
4. Transcrever com `helpers/transcribe.py` ou usar transcrição cacheada.
5. Rodar `helpers/pack_transcripts.py`.
6. Criar `edl.json`.
7. Rodar `helpers/edl_boundary_audit.py`.
8. Renderizar com `helpers/render.py` ou exportar XML com `helpers/export_premiere_xml.py`.

Para anúncios, ler também:

- `skills/ad-corpus-study/references/golden-editing-standard.md`
- `skills/ad-copy-structure/SKILL.md`
- `skills/ad-editorial-decupagem/SKILL.md`
- `skills/ad-corpus-study/references/corpus-notes.md`
- `skills/ad-corpus-study/references/ad-editing-qc.md`

## Exportar XML Para Premiere

Premiere não precisa estar aberto para gerar XML.

```bash
python helpers/export_premiere_xml.py edit/edl.json \
  -o edit/premiere_export.xml \
  --sequence-name MinhaSequencia
```

Depois importe no Premiere via `File > Import`.

## Verificação

```bash
python helpers/transcribe.py --help
python helpers/pack_transcripts.py --help
python helpers/render.py --help
python helpers/remove_silence.py --help
python helpers/export_premiere_xml.py --help
python -m unittest tests.test_remove_silence_auto_profile -v
```
