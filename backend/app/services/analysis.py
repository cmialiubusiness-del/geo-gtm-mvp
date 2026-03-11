from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.core.enums import (
    ClaimRiskLevel,
    ClaimSentiment,
    ClaimSubjectType,
    PromptCategory,
)

RISK_TIER = ("诈骗", "违法", "无牌照", "被查", "黑名单", "跑路")
COMPLAINT_TIER = ("投诉", "差评", "隐形收费", "服务差", "坑")
PRICE_TIER = ("贵", "收费高", "报价高", "年费高")
WEAK_NEGATIVE_TIER = ("一般", "不如", "尚可", "偏慢", "未排入前三")

POSITIVE_STRONG = ("首选", "推荐", "专业", "透明", "高效", "稳妥", "靠谱", "经验丰富", "合规", "口碑好")
POSITIVE_MILD = ("清晰", "及时", "细致", "稳定", "省心", "熟悉")
FACTUAL_CUES = ("提供", "包含", "通常", "资料清单", "流程", "支持", "需要", "可办理", "有牌照")

RANK_RE = re.compile(r"^\s*(?P<num>\d+)\s*[\.\)\-、]\s*(?P<body>.+)$")
CN_RANK_RE = re.compile(r"^\s*第(?P<cn>[一二三四五六七八九十])\s*[:：]?\s*(?P<body>.+)$")
CN_NUM_MAP = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


@dataclass(frozen=True)
class EntityConfig:
    name: str
    aliases: list[str]
    subject_type: ClaimSubjectType

    @property
    def variants(self) -> list[str]:
        seen: list[str] = []
        for raw in [self.name, *self.aliases]:
            token = raw.strip()
            if token and token not in seen:
                seen.append(token)
        return seen


@dataclass(frozen=True)
class ClaimDraft:
    subject_type: ClaimSubjectType
    subject_name: str
    claim_text: str
    sentiment: ClaimSentiment
    impact_score: int
    risk_level: ClaimRiskLevel
    is_factual_assertion: bool
    category: PromptCategory


@dataclass(frozen=True)
class AnalysisResult:
    ranks: dict[str, int]
    claims: list[ClaimDraft]
    hijack_flag: bool
    hijack_strength: int
    recommended_entities: list[str]
    brand_present: bool


def normalize_text(text: str) -> str:
    return text.lower().strip()


def text_mentions(text: str, entity: EntityConfig) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(variant) in normalized for variant in entity.variants)


def split_text_units(raw_text: str) -> list[str]:
    units: list[str] = []
    for line in re.split(r"[\r\n]+", raw_text):
        clean_line = line.strip()
        if not clean_line:
            continue
        if re.match(r"^\s*([\-\*\u2022]|\d+\s*[\.\)\-、]|第[一二三四五六七八九十])", clean_line):
            units.append(clean_line)
            continue
        pieces = [piece.strip() for piece in re.split(r"(?<=[。！？!?；;])", clean_line) if piece.strip()]
        units.extend(pieces or [clean_line])
    return units


def is_factual_assertion(text: str) -> bool:
    normalized = normalize_text(text)
    return any(token in normalized for token in FACTUAL_CUES)


def classify_sentiment(text: str) -> ClaimSentiment:
    normalized = normalize_text(text)
    pos_score = 0
    neg_score = 0

    for token in POSITIVE_STRONG:
        if token in normalized:
            pos_score += 2
    for token in POSITIVE_MILD:
        if token in normalized:
            pos_score += 1
    for token in RISK_TIER:
        if token in normalized:
            neg_score += 3
    for token in COMPLAINT_TIER:
        if token in normalized:
            neg_score += 2
    for token in PRICE_TIER:
        if token in normalized:
            neg_score += 1
    for token in WEAK_NEGATIVE_TIER:
        if token in normalized:
            neg_score += 1
    if "不建议" in normalized or "谨慎" in normalized:
        neg_score += 2

    if neg_score > pos_score and neg_score > 0:
        return ClaimSentiment.negative
    if pos_score > neg_score and pos_score > 0:
        return ClaimSentiment.positive
    return ClaimSentiment.neutral


def score_impact(text: str, sentiment: ClaimSentiment | None = None) -> int:
    normalized = normalize_text(text)
    resolved_sentiment = sentiment or classify_sentiment(normalized)

    score = 0
    if any(token in normalized for token in RISK_TIER):
        score += 60
    if any(token in normalized for token in COMPLAINT_TIER):
        score += 35
    if any(token in normalized for token in PRICE_TIER):
        score += 20
    if any(token in normalized for token in WEAK_NEGATIVE_TIER):
        score += 10

    if resolved_sentiment == ClaimSentiment.positive:
        if any(token in normalized for token in POSITIVE_STRONG):
            score = max(score, 25)
        elif any(token in normalized for token in POSITIVE_MILD):
            score = max(score, 15)
        else:
            score = max(score, 10)
    elif resolved_sentiment == ClaimSentiment.neutral:
        if score == 0 and is_factual_assertion(normalized):
            score = 5
        if "风险" in normalized or "谨慎" in normalized:
            score = max(score, 20)

    return min(score, 100)


def determine_risk_level(
    sentiment: ClaimSentiment, impact_score: int, text: str
) -> ClaimRiskLevel:
    normalized = normalize_text(text)
    if sentiment == ClaimSentiment.negative:
        if impact_score >= 80:
            return ClaimRiskLevel.critical
        if impact_score >= 50:
            return ClaimRiskLevel.high
        if impact_score >= 20:
            return ClaimRiskLevel.medium
        return ClaimRiskLevel.low

    if sentiment == ClaimSentiment.neutral and ("风险" in normalized or "谨慎" in normalized):
        return ClaimRiskLevel.medium
    return ClaimRiskLevel.low


def parse_rankings(raw_text: str, entities: list[EntityConfig]) -> dict[str, int]:
    rankings: dict[str, int] = {}
    for line in re.split(r"[\r\n]+", raw_text):
        line = line.strip()
        if not line:
            continue

        rank: int | None = None
        match = RANK_RE.match(line)
        if match:
            rank = int(match.group("num"))
            body = match.group("body")
        else:
            cn_match = CN_RANK_RE.match(line)
            if not cn_match:
                continue
            rank = CN_NUM_MAP.get(cn_match.group("cn"))
            body = cn_match.group("body")

        if rank is None:
            continue

        for entity in entities:
            if text_mentions(body, entity):
                current = rankings.get(entity.name)
                rankings[entity.name] = rank if current is None else min(current, rank)
    return rankings


def _rank_line_body(text: str) -> str | None:
    match = RANK_RE.match(text)
    if match:
        return match.group("body").strip()
    cn_match = CN_RANK_RE.match(text)
    if cn_match:
        return cn_match.group("body").strip()
    return None


def _is_pure_rank_line_for_entity(text: str, entity: EntityConfig) -> bool:
    body = _rank_line_body(text)
    if body is None:
        return False
    normalized_body = re.sub(r"[\s：:，,。.!！?？\-_/（）()]+", "", normalize_text(body))
    if not normalized_body:
        return False
    for variant in entity.variants:
        normalized_variant = re.sub(
            r"[\s：:，,。.!！?？\-_/（）()]+",
            "",
            normalize_text(variant),
        )
        if normalized_variant and normalized_body == normalized_variant:
            return True
    return False


def extract_claims(
    raw_text: str,
    brand: EntityConfig,
    competitors: list[EntityConfig],
    category: PromptCategory,
) -> list[ClaimDraft]:
    relevant_claims: list[ClaimDraft] = []
    entities = [brand, *competitors]

    for unit in split_text_units(raw_text):
        for entity in entities:
            if not text_mentions(unit, entity):
                continue
            if _is_pure_rank_line_for_entity(unit, entity):
                continue
            sentiment = classify_sentiment(unit)
            impact_score = score_impact(unit, sentiment)
            relevant_claims.append(
                ClaimDraft(
                    subject_type=entity.subject_type,
                    subject_name=entity.name,
                    claim_text=unit,
                    sentiment=sentiment,
                    impact_score=impact_score,
                    risk_level=determine_risk_level(sentiment, impact_score, unit),
                    is_factual_assertion=is_factual_assertion(unit),
                    category=category,
                )
            )
    return relevant_claims


def is_brand_intent(prompt_text: str, brand: EntityConfig, brand_topics: list[str] | None = None) -> bool:
    topics = [*brand.variants, *(brand_topics or [])]
    prompt_lower = normalize_text(prompt_text)
    return any(normalize_text(topic) in prompt_lower for topic in topics if topic)


def detect_hijack(
    prompt_text: str,
    brand: EntityConfig,
    competitors: list[EntityConfig],
    rankings: dict[str, int],
    raw_text: str,
    brand_topics: list[str] | None = None,
) -> tuple[bool, int, list[str], bool]:
    brand_present = text_mentions(raw_text, brand)
    if not is_brand_intent(prompt_text, brand, brand_topics):
        return False, 0, [], brand_present

    competitor_ranks = {
        competitor.name: rankings[competitor.name]
        for competitor in competitors
        if competitor.name in rankings and rankings[competitor.name] <= 3
    }
    if not competitor_ranks:
        return False, 0, [], brand_present

    recommended_entities = [
        name for name, _ in sorted(competitor_ranks.items(), key=lambda item: item[1])[:3]
    ]

    brand_rank = rankings.get(brand.name)
    if not brand_present and any(rank == 1 for rank in competitor_ranks.values()):
        return True, 100, recommended_entities, False
    if not brand_present and any(rank in (2, 3) for rank in competitor_ranks.values()):
        return True, 70, recommended_entities, False
    if brand_rank and brand_rank > 3:
        return True, 40, recommended_entities, True
    return False, 0, recommended_entities, brand_present


def analyze_answer(
    prompt_text: str,
    raw_text: str,
    category: PromptCategory,
    brand: EntityConfig,
    competitors: list[EntityConfig],
    brand_topics: list[str] | None = None,
) -> AnalysisResult:
    entities = [brand, *competitors]
    rankings = parse_rankings(raw_text, entities)
    claims = extract_claims(raw_text, brand, competitors, category)
    hijack_flag, hijack_strength, recommended_entities, brand_present = detect_hijack(
        prompt_text, brand, competitors, rankings, raw_text, brand_topics
    )
    return AnalysisResult(
        ranks=rankings,
        claims=claims,
        hijack_flag=hijack_flag,
        hijack_strength=hijack_strength,
        recommended_entities=recommended_entities,
        brand_present=brand_present,
    )


def capability_label(score: float) -> str:
    if score >= 80:
        return "强优势"
    if score >= 60:
        return "优势"
    if score >= 40:
        return "中性"
    if score >= 20:
        return "劣势"
    return "严重劣势"


def compute_capability_scores(
    records: list[dict[str, Any]],
    prompt_counts_by_category: dict[str, int],
    runs_count: int,
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    denominator_runs = max(runs_count, 1)

    for category in PromptCategory:
        key = category.value
        category_records = [record for record in records if record["category"] == key]
        pos_sum = sum(
            int(record["impact_score"])
            for record in category_records
            if record["sentiment"] == ClaimSentiment.positive.value
        )
        neg_sum = sum(
            int(record["impact_score"])
            for record in category_records
            if record["sentiment"] == ClaimSentiment.negative.value
        )
        prompt_count = max(prompt_counts_by_category.get(key, 1), 1)
        normalizer = prompt_count * denominator_runs
        score = max(0.0, min(100.0, 50.0 + (pos_sum - neg_sum) / normalizer))

        positive_claims = sorted(
            [record for record in category_records if record["sentiment"] == ClaimSentiment.positive.value],
            key=lambda item: int(item["impact_score"]),
            reverse=True,
        )[:2]
        negative_claims = sorted(
            [record for record in category_records if record["sentiment"] == ClaimSentiment.negative.value],
            key=lambda item: int(item["impact_score"]),
            reverse=True,
        )[:2]

        results[key] = {
            "category": key,
            "score": round(score, 2),
            "label": capability_label(score),
            "top_positive_claims": [claim["claim_text"] for claim in positive_claims],
            "top_negative_claims": [claim["claim_text"] for claim in negative_claims],
        }

    return results
