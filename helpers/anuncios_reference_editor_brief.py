"""Generate an editorial briefing from corpus reference signals.

Usage:
    python helpers/anuncios_reference_editor_brief.py Anuncios/8104/Ad8104_Final.txt
    python helpers/anuncios_reference_editor_brief.py Anuncios/8104/Ad8104_Final.txt --format markdown
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import anuncios_reference_anchor_brief as arab
import anuncios_hybrid_matrix as ahm
import anuncios_reference_policy as arp


FUNNEL_GUIDANCE = {
    "nine_premium_ais": {
        "arc": "price anchor -> flagship premium tools -> stacked cost -> surprising condition -> CTA",
        "must_preserve": [
            "quantity claim such as 9 or nove das melhores",
            "named flagship tools when present",
            "stacked monthly cost logic",
            "free-for-a-year or premium-access framing",
            "the single gating condition",
        ],
        "common_damage": [
            "dropping the cost anchor",
            "removing named tools and keeping only generic categories",
            "flattening the surprise around the condition",
        ],
    },
    "pdf_gabarito": {
        "arc": "curiosity or authority hook -> attach the PDF -> better answers -> proof details -> CTA",
        "must_preserve": [
            "PDF as the concrete object",
            "attach or upload mechanism",
            "proof details such as one page, 600 words, 4 mil artigos, 20 tecnicas",
            "relief that the user does not need to read it",
        ],
        "common_damage": [
            "turning PDF into a generic file or document",
            "cutting the scientific proof block when it justifies the mechanism",
            "removing the ease claim",
        ],
    },
    "cancel_chatgpt": {
        "arc": "cancel ChatGPT hook -> one model is not enough -> bundle logic -> comparison/proof -> CTA",
        "must_preserve": [
            "cancellation or refusal hook",
            "named models and why each matters",
            "bundle-versus-single-model value logic",
            "trial, guarantee, or price-risk logic",
        ],
        "common_damage": [
            "weakening the anti-ChatGPT hook",
            "cutting the per-model use cases",
            "duplicating the CTA after the guarantee block",
        ],
    },
    "ranking_adaptapass": {
        "arc": "external ranking -> judgments on tools -> Adapta Pass absorbs winners -> business payoff -> CTA",
        "must_preserve": [
            "the ranking premise",
            "at least a few concrete rank judgments",
            "why Adapta Pass is different",
            "the first-place or excellent payoff",
        ],
        "common_damage": [
            "cutting so many ranked examples that the ranking stops making sense",
            "replacing first-place payoff with vague praise",
        ],
    },
    "empresa_nativa_ia": {
        "arc": "qualifier -> authority -> transformation promise -> special program -> CTA",
        "must_preserve": [
            "qualifier threshold such as revenue cutoff",
            "empresa nativa de IA concept",
            "authority proof",
            "special-program positioning",
        ],
        "common_damage": [
            "deleting the qualifier and making the ad broad",
            "replacing transformation with generic productivity language",
        ],
    },
    "medico_nativo_ia": {
        "arc": "specialist authority -> native-IA identity shift -> consultorio mechanism -> time/revenue payoff -> CTA",
        "must_preserve": [
            "medical or clinical qualifier when present",
            "the native-IA or transplante de IA concept",
            "concrete consultorio mechanisms such as prontuario, agenda, anamnese, WhatsApp, follow-up",
            "time, capacity, or revenue payoff",
            "named authority such as Paulo Muzy when present",
        ],
        "common_damage": [
            "replacing the clinical mechanism with generic productivity language",
            "deleting the identity shift that makes the offer feel urgent",
            "removing specialist proof and leaving only generic AI hype",
        ],
    },
    "desafio_programa_ia": {
        "arc": "challenge invitation -> day-by-day promise -> operational business payoff -> urgency to join -> CTA",
        "must_preserve": [
            "the challenge format itself",
            "who the challenge is for, such as lawyers or active subscribers",
            "the day-by-day or task-by-task mechanism when present",
            "the concrete business payoff",
            "the join path such as button, group, or invite timing",
        ],
        "common_damage": [
            "removing the challenge mechanic and leaving only generic AI hype",
            "cutting the target professional qualifier",
            "flattening the day-by-day promise into a vague summary",
        ],
    },
    "trial_update_pack": {
        "arc": "objection or update hook -> biggest pack/new platform -> risk-free test -> bonuses or proof -> CTA",
        "must_preserve": [
            "the 30-day or risk-free test mechanism",
            "the update-pack or new-platform novelty",
            "named proof such as new tools, features, or bonuses",
            "the no-risk or refund logic",
        ],
        "common_damage": [
            "keeping only generic value talk and deleting the no-risk mechanism",
            "removing the update-pack novelty that justifies the offer",
            "losing the concrete CTA path into the trial",
        ],
    },
    "whisper_secret": {
        "arc": "come closer secret hook -> free claim -> single condition -> scarcity whisper -> urgent CTA",
        "must_preserve": [
            "intimate or whispered hook",
            "exact free claim",
            "single-condition turn",
            "urgent closing fragments such as vai, clica",
        ],
        "common_damage": [
            "normalizing the whisper hook into plain speech",
            "removing the final rhythmic imperative",
        ],
    },
    "anti_free_premium_status": {
        "arc": "status threat -> free tool humiliation -> degradation proof -> premium necessity -> rescue offer -> CTA",
        "must_preserve": [
            "status-threat opener",
            "concrete degradation proof",
            "bridge from problem pressure into rescue offer",
            "specific rescue offer details",
            "the gate or prerequisite",
        ],
        "common_damage": [
            "stopping at the problem and never landing the rescue offer",
            "keeping the pressure but deleting the mechanism",
            "softening the direct-response edge too much",
        ],
    },
    "authority_watch_report_back": {
        "arc": "personal confession -> borrowed authority -> named mechanisms -> ask for validation -> hidden-access CTA",
        "must_preserve": [
            "personal confession or request for help",
            "authority anchor such as a known figure",
            "named mechanisms and proof details",
            "watch-and-report-back loop",
            "hidden-access CTA",
        ],
        "common_damage": [
            "normalizing the opener into a generic recommendation",
            "compressing named techniques into vague productivity claims",
            "losing the validation loop that powers the CTA",
        ],
    },
    "summit_event": {
        "arc": "scarcity hook -> prior sold-out proof -> bigger edition -> anti-event turn -> qualification -> CTA",
        "must_preserve": [
            "sold-out hook",
            "chronology and scale proof",
            "anti-event framing",
            "qualification/filter logic",
            "CTA path into the event",
        ],
        "common_damage": [
            "replacing anti-event angle with generic hype",
            "deleting the qualification turn",
            "flattening chronology into summary",
        ],
    },
    "unknown": {
        "arc": "Hook -> Lead -> Body -> Proof -> CTA",
        "must_preserve": [
            "the real hook",
            "the sales mechanism",
            "the proof block",
            "a single final CTA",
        ],
        "common_damage": [
            "keeping structure but deleting the mechanism",
            "duplicating proof or CTA",
        ],
    },
}


POLICY_BEHAVIOR = {
    "follow_closely": [
        "treat the reference as a strong editorial guide for both structure and wording",
        "use the safe anchors as an active spine, not as optional inspiration",
        "still prefer the bruto when the reference would force obvious set noise or ASR corruption",
    ],
    "use_with_review": [
        "use the reference confidently for structure",
        "use only light wording pull from the safe anchors",
        "review for flattening, truncation, or duplicated meaning before trusting the reference literally",
    ],
    "prefer_bruto": [
        "treat the bruto as the main truth source",
        "use the reference only as a weak hint",
        "do not imitate reference wording or structure when it weakens the commercial logic",
    ],
    "learn_structure_not_middle_wording": [
        "borrow structure and transitions from the reference",
        "use only edge anchors if they help keep the opening or close sharp",
        "rebuild the middle from the bruto instead of copying reference wording",
    ],
    "funnel_only": [
        "use the reference only to understand the funnel and promise type",
        "derive wording almost entirely from the bruto",
        "do not use wording anchors from the reference",
    ],
    "alternate_hook_only": [
        "treat the reference opener as an alternate strategy only",
        "keep the rest of the cut anchored to the bruto",
        "do not let the alternate hook dominate the whole ad",
    ],
    "alternate_cta_only": [
        "treat the reference close as an alternate CTA strategy only",
        "keep the rest of the cut anchored to the bruto",
        "do not let the alternate CTA dominate the whole ad",
    ],
}


HYBRID_RISK_GUIDANCE = {
    "benign_overlap": [
        "overlap between these two funnel families is common and usually safe",
        "keep the dominant funnel in charge, but do not delete concrete details that naturally support the secondary read",
    ],
    "review_overlap": [
        "this overlap is common enough to expect, but it can still cause subtle editorial drift",
        "use the dominant funnel for structure, then verify that concrete mechanism, proof, and CTA details still match the actual copy rather than the neighboring family",
    ],
    "dangerous_overlap": [
        "this funnel overlap is a known source of bad cuts and false certainty",
        "do not borrow wording casually from the reference; confirm the real selling mechanism, proof block, and CTA path from the bruto before finalizing",
        "treat any missing or swapped load-bearing detail as a blocking QC failure, not a cosmetic issue",
    ],
    "unknown": [
        "no calibrated hybrid-pair risk was found for this combination",
        "if the ad still feels split across families, validate the commercial arc from the actual copy instead of assuming the house overlap is safe",
    ],
}


def infer_bruto_path(final_path: Path) -> Path:
    return final_path.with_name(final_path.name.replace("_Final.txt", "_Bruto.txt"))


def build_editor_brief(final_path: Path) -> dict:
    policy = arp.recommend(final_path)
    anchors = arab.build_anchor_brief(final_path)
    funnel = policy["funnel"]
    funnel_guidance = FUNNEL_GUIDANCE.get(funnel, FUNNEL_GUIDANCE["unknown"])
    bruto_path = infer_bruto_path(final_path)
    hybrid_risk = policy["hybrid_risk"] or "unknown"
    hybrid_row = None
    if policy["hybrid_candidate"] and policy["funnel_second_choice"]:
        matrix_rows = ahm.load_matrix()
        hybrid_row = ahm.lookup_pair(matrix_rows, policy["funnel"], policy["funnel_second_choice"])
    hybrid_guidance = HYBRID_RISK_GUIDANCE[hybrid_risk]

    reference_role = (
        f"Policy `{policy['policy']}` with wording weight {policy['wording_weight']:.2f} "
        f"and structure weight {policy['structure_weight']:.2f}."
    )
    if policy["funnel_confidence"] != "high":
        reference_role += f" Funnel confidence is `{policy['funnel_confidence']}`."

    agent_checks = [
        "preserve a complete commercial arc: Hook -> Lead -> Body -> Proof -> CTA",
        "keep concrete offer details when they are load-bearing for this funnel",
        "remove resets, set talk, literal repetition, semantic echo, and dead air",
        "leave only one clean CTA unless repetition is clearly intentional",
        "repair obvious high-confidence ASR corruption in names, brands, products, or channels when context makes the intended meaning clear",
    ]

    if policy["policy"] in {"follow_closely", "use_with_review"}:
        agent_checks.append("compare your chosen hook and close against the safe anchors before finalizing")
    if policy["policy"] == "learn_structure_not_middle_wording":
        agent_checks.append("do not force the middle body to match the reference wording")
    if policy["policy"] == "funnel_only":
        agent_checks.append("treat any low similarity to the reference as expected, not as a failure by itself")
    if policy["funnel_confidence"] in {"low", "unknown"}:
        agent_checks.append("because funnel confidence is low, validate the commercial arc from the copy itself instead of leaning too hard on house-family assumptions")
    if policy["hybrid_candidate"] and policy["funnel_second_choice"]:
        agent_checks.append(
            f"this looks hybrid; preserve concrete details that support both `{policy['funnel']}` and `{policy['funnel_second_choice']}` when they are load-bearing"
        )
        if hybrid_risk == "review_overlap":
            agent_checks.append(
                "because this hybrid pair is review-risk, confirm that the mechanism and proof belong to the dominant funnel before approving the cut"
            )
        elif hybrid_risk == "dangerous_overlap":
            agent_checks.append(
                "because this hybrid pair is dangerous, explicitly verify that the hook, mechanism, and CTA path all belong to the same real ad and were not cross-contaminated from a neighboring funnel"
            )

    prompt_block_lines = [
        "Reference-derived editorial brief:",
        f"- Funnel: {funnel}",
        f"- Expected arc: {funnel_guidance['arc']}",
        f"- Funnel confidence: {policy['funnel_confidence']}",
        f"- Reference label: {policy['reference_label']}",
        f"- Rewrite subtype: {policy['rewrite_subtype']}",
        f"- Policy: {policy['policy']}",
        f"- Reference role: {reference_role}",
    ]
    if policy["funnel_second_choice"]:
        prompt_block_lines.append(f"- Second funnel candidate: {policy['funnel_second_choice']}")
    if policy["hybrid_candidate"]:
        prompt_block_lines.append(f"- Hybrid overlap risk: {hybrid_risk}")
        prompt_block_lines.append("- Hybrid overlap guidance:")
        prompt_block_lines.extend(f"  - {item}" for item in hybrid_guidance)
    prompt_block_lines.append("- How to use the reference:")
    prompt_block_lines.extend(f"  - {item}" for item in POLICY_BEHAVIOR[policy["policy"]])
    prompt_block_lines.append("- Funnel details to preserve:")
    prompt_block_lines.extend(f"  - {item}" for item in funnel_guidance["must_preserve"])
    prompt_block_lines.append("- Common failure modes to avoid:")
    prompt_block_lines.extend(f"  - {item}" for item in funnel_guidance["common_damage"])
    if anchors["anchors"]:
        prompt_block_lines.append("- Safe anchors from the reference:")
        prompt_block_lines.extend(f"  - {item}" for item in anchors["anchors"])
    else:
        prompt_block_lines.append("- Safe anchors from the reference: none")
    prompt_block_lines.append("- Final QC checks:")
    prompt_block_lines.extend(f"  - {item}" for item in agent_checks)

    return {
        "final_path": str(final_path),
        "bruto_path": str(bruto_path),
        "funnel": funnel,
        "funnel_confidence": policy["funnel_confidence"],
        "funnel_second_choice": policy["funnel_second_choice"],
        "funnel_score_margin": policy["funnel_score_margin"],
        "hybrid_candidate": policy["hybrid_candidate"],
        "hybrid_risk": hybrid_risk if policy["hybrid_candidate"] else None,
        "hybrid_guidance": hybrid_guidance if policy["hybrid_candidate"] else [],
        "hybrid_pair": hybrid_row["pair"] if hybrid_row and policy["hybrid_candidate"] else None,
        "expected_arc": funnel_guidance["arc"],
        "reference_label": policy["reference_label"],
        "rewrite_subtype": policy["rewrite_subtype"],
        "policy": policy["policy"],
        "anchor_mode": policy["anchor_mode"],
        "wording_weight": policy["wording_weight"],
        "structure_weight": policy["structure_weight"],
        "reference_role": reference_role,
        "policy_notes": policy["notes"],
        "policy_instructions": POLICY_BEHAVIOR[policy["policy"]],
        "editorial_instruction": policy["editorial_instruction"],
        "must_preserve": funnel_guidance["must_preserve"],
        "common_damage": funnel_guidance["common_damage"],
        "safe_anchor_strategy": anchors["anchor_strategy"],
        "safe_anchors": anchors["anchors"],
        "agent_qc_checks": agent_checks,
        "prompt_block": "\n".join(prompt_block_lines),
    }


def as_markdown(brief: dict) -> str:
    lines = [
        "# Reference Editor Brief",
        "",
        f"- Final: `{brief['final_path']}`",
        f"- Bruto: `{brief['bruto_path']}`",
        f"- Funnel: `{brief['funnel']}`",
        f"- Funnel confidence: `{brief['funnel_confidence']}`",
        f"- Expected arc: `{brief['expected_arc']}`",
        f"- Reference label: `{brief['reference_label']}`",
        f"- Rewrite subtype: `{brief['rewrite_subtype']}`",
        f"- Policy: `{brief['policy']}`",
        f"- Anchor mode: `{brief['anchor_mode']}`",
        f"- Wording weight: `{brief['wording_weight']}`",
        f"- Structure weight: `{brief['structure_weight']}`",
        "",
        "## How to use the reference",
    ]
    if brief["funnel_second_choice"]:
        lines.insert(10, f"- Second funnel candidate: `{brief['funnel_second_choice']}`")
    if brief["hybrid_candidate"]:
        lines.insert(11, "- Hybrid candidate: `true`")
        lines.insert(12, f"- Hybrid risk: `{brief['hybrid_risk']}`")
    lines.extend(f"- {item}" for item in brief["policy_instructions"])
    if brief["hybrid_guidance"]:
        lines.extend(["", "## Hybrid guidance"])
        lines.extend(f"- {item}" for item in brief["hybrid_guidance"])
    lines.extend(["", "## Must preserve"])
    lines.extend(f"- {item}" for item in brief["must_preserve"])
    lines.extend(["", "## Common damage"])
    lines.extend(f"- {item}" for item in brief["common_damage"])
    lines.extend(["", "## Safe anchors"])
    if brief["safe_anchors"]:
        lines.extend(f"- {item}" for item in brief["safe_anchors"])
    else:
        lines.append("- none")
    lines.extend(["", "## Agent QC"])
    lines.extend(f"- {item}" for item in brief["agent_qc_checks"])
    lines.extend(["", "## Prompt Block", "", "```text", brief["prompt_block"], "```"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a compact editorial brief from reference signals.")
    parser.add_argument("path", help="Specific Ad*_Final.txt path")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    brief = build_editor_brief(Path(args.path))
    if args.format == "markdown":
        print(as_markdown(brief))
        return
    print(json.dumps(brief, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
