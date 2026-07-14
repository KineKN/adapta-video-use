"""Classify Adapta ad transcripts into recurring funnel families.

Usage:
    python helpers/anuncios_funnel_classifier.py path/to/AdXXXX_Bruto.txt
    python helpers/anuncios_funnel_classifier.py --root Anuncios --top 50
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class FunnelMatch:
    name: str
    score: int
    matched_patterns: list[str]


FUNNELS: dict[str, list[str]] = {
    "nine_premium_ais": [
        r"\bnove\b|\b9\b",
        r"premium|vers[aã]o paga|pagas",
        r"gpt|claude|gemini|grok|perplexity",
        r"condi[cç][aã]o|pr[eé]-requisito",
    ],
    "pdf_gabarito": [
        r"\bpdf\b",
        r"gabarito|documento de uma p[aá]gina|600 palavras",
        r"4 mil artigos|20 t[eé]cnicas|artigos cient[ií]ficos",
        r"anexa|subir|anexar",
    ],
    "cancel_chatgpt": [
        r"cancelei|me recuso a pagar|cancelam o chatgpt",
        r"chatgpt",
        r"gpt|claude|gemini|grok|perplexity",
    ],
    "ranking_adaptapass": [
        r"ranking",
        r"adapta pass",
        r"excelente|primeiro lugar|n[aã]o [ée] s[oó] uma ia",
    ],
    "empresa_nativa_ia": [
        r"empresa nativa de ia|nativa de ia",
        r"2 milh|milh[oõ]es por ano|fatura mais de um milh[aã]o|fatura mais de 2",
        r"adapta pass|mil empresas|100 mil reais|tomador de decis[aã]o|implementa[rç][aã]o de ia na empresa|implementar ia no seu neg[oó]cio|programa dedicado para implementar",
        r"empresa n[aã]o precisa de mais funcion[aá]rios|automa[cç][oõ]es rodando|gargalos certos|agentes inteligentes trabalhando 24 horas|aumentar a margem sem aumentar a sua equipe",
    ],
    "whisper_secret": [
        r"chega mais perto|n[aã]o quero que muita gente saiba|sussurr",
        r"nove das melhores|de gr[aá]ca",
        r"vai, clica|clica r[aá]pido|antes que algu[eé]m escute",
    ],
    "summit_event": [
        r"adapta summit|anti-?evento|anti evento",
        r"sold out|esgot|ingressos?|4 mil|5 mil|7 mil|lote",
        r"oficinas|sala de vidro|palco|patroc[ií]nios?|empres[aá]rios|neg[oó]cios",
        r"manda o site|garantir o ingresso|conseguir sua vaga|31 de julho|1 de agosto|um de agosto",
    ],
    "anti_free_premium_status": [
        r"gratuit[ao]|chatgpt de gr[aá]ca|capad[ao]",
        r"ceo da openai|hor[aá]rio de pico|priorizar quem paga|mediocre|frouxo",
        r"premium|condi[cç][aã]o|pr[eé]-requisito",
    ],
    "authority_watch_report_back": [
        r"renato cariani|cariani",
        r"doping de trabalho|modo detetive|12 palavras",
        r"me fala|me conta|volta aqui nos coment[aá]rios|estou viajando",
    ],
    "medico_nativo_ia": [
        r"m[eé]dic[oa]s?|cirurgi[aã]o|consult[oó]rio|prontu[aá]rio|anamnese",
        r"paulo muzy|muzy|transplante de (ia|intelig[eê]ncia artificial)|m[eé]dico nativo de (ia|ar)",
        r"paciente no whatsapp|agenda|follow-?up|consulta|diagn[oó]stic|cl[ií]nica",
        r"mais de um milh[aã]o|dobro|atendendo menos|devolver .* horas por semana",
    ],
    "desafio_programa_ia": [
        r"desafio de (2|dois|5|cinco) dias|desafio gratuito|grupo oficial do desafio|convite oficial do desafio",
        r"uma tarefa por dia|uma ia por dia|assinantes ativos|grupo de whatsapp|quinta-feira .*8 horas",
        r"advogad|escrit[oó]rio|captar clientes|linkedin|resumo executivo|assistente de reuni[aã]o",
        r"vaga no desafio|garante sua vaga|resgatar .* desafio|come[aç]a hoje|come[aç]a amanh[aã]",
    ],
    "trial_update_pack": [
        r"30 dias|teste sem risco|sem risco|n[aã]o gostar.*devolve|devolvemos? .* dinheiro|garantia",
        r"maior pacote de atualiza[cç][oõ]es|one26|nova plataforma|novas funcionalidades|presentes extras|kit de comemora[cç][aã]o",
        r"150 mil assinantes|anivers[aá]rio|3 anos de empresa|pacote de atualiza[cç][oõ]es",
        r"testar tudo isso|teste completo|condi[cç][aã]o limitada|sem custo adicional",
    ],
}

PRIORITY_OVERRIDES = [
    ("whisper_secret", 3, "nine_premium_ais"),
    ("ranking_adaptapass", 2, "cancel_chatgpt"),
    ("anti_free_premium_status", 2, "nine_premium_ais"),
    ("authority_watch_report_back", 2, "cancel_chatgpt"),
    ("summit_event", 2, "empresa_nativa_ia"),
    ("medico_nativo_ia", 2, "empresa_nativa_ia"),
    ("medico_nativo_ia", 2, "authority_watch_report_back"),
    ("desafio_programa_ia", 2, "empresa_nativa_ia"),
    ("desafio_programa_ia", 2, "summit_event"),
    ("trial_update_pack", 2, "empresa_nativa_ia"),
    ("trial_update_pack", 2, "nine_premium_ais"),
]


def classify_confidence(matches: list[FunnelMatch], top_name: str) -> tuple[str, int | None, str | None, bool]:
    if not matches:
        return "unknown", None, None, False

    top_score = matches[0].score
    top_candidates = [match.name for match in matches if match.score == top_score]
    second_score = matches[1].score if len(matches) > 1 else None
    second_name = matches[1].name if len(matches) > 1 else None
    hybrid_candidate = len(top_candidates) > 1 or (second_score is not None and top_score - second_score <= 1)

    if top_name == "unknown":
        return "unknown", second_score, second_name, hybrid_candidate
    if second_score is None and top_score >= 2:
        return "high", second_score, second_name, False
    if top_score >= 3 and (second_score is None or top_score - second_score >= 1):
        return "high", second_score, second_name, hybrid_candidate
    if top_score >= 2:
        return "medium", second_score, second_name, hybrid_candidate
    return "low", second_score, second_name, hybrid_candidate


def score_text(text: str) -> list[FunnelMatch]:
    lowered = text.lower()
    matches: list[FunnelMatch] = []
    for name, patterns in FUNNELS.items():
        hit_patterns = [pattern for pattern in patterns if re.search(pattern, lowered)]
        if hit_patterns:
            matches.append(
                FunnelMatch(
                    name=name,
                    score=len(hit_patterns),
                    matched_patterns=hit_patterns,
                )
            )
    return sorted(matches, key=lambda item: item.score, reverse=True)


def classify_path(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    matches = score_text(text)
    top_name = matches[0].name if matches else "unknown"
    scores = {match.name: match.score for match in matches}
    for preferred, min_score, fallback in PRIORITY_OVERRIDES:
        if scores.get(preferred, 0) >= min_score and top_name == fallback:
            top_name = preferred
    top_score = scores.get(top_name, 0)
    top_match = next((match for match in matches if match.name == top_name), None)
    second_score = None
    second_name = None
    for match in matches:
        if match.name != top_name:
            second_score = match.score
            second_name = match.name
            break
    confidence, raw_second_score, raw_second_name, hybrid_candidate = classify_confidence(matches, top_name)
    if second_score is None:
        second_score = raw_second_score
        second_name = raw_second_name
    return {
        "path": str(path),
        "top_funnel": top_name,
        "top_score": top_score,
        "second_funnel": second_name,
        "second_score": second_score,
        "score_margin": None if second_score is None else top_score - second_score,
        "funnel_confidence": confidence,
        "hybrid_candidate": hybrid_candidate,
        "top_matched_patterns": [] if top_match is None else top_match.matched_patterns,
        "matches": [asdict(match) for match in matches],
    }


def iter_paths(root: Path) -> list[Path]:
    return sorted(root.glob("*/*_Bruto.txt")) + sorted(root.glob("*/*_Final.txt"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify Adapta ad funnels.")
    parser.add_argument("path", nargs="?", help="Specific transcript path")
    parser.add_argument("--root", help="Corpus root to scan")
    parser.add_argument("--top", type=int, default=25, help="Max rows to print in root mode")
    args = parser.parse_args()

    if args.path:
        print(json.dumps(classify_path(Path(args.path)), ensure_ascii=False, indent=2))
        return

    if not args.root:
        raise SystemExit("Provide either a transcript path or --root.")

    rows = [classify_path(path) for path in iter_paths(Path(args.root))]
    for row in rows[: args.top]:
        print(f"{row['top_funnel']}: {row['path']}")


if __name__ == "__main__":
    main()
