from app.core.enums import ClaimSentiment, ClaimSubjectType, PromptCategory
from app.services.analysis import (
    EntityConfig,
    analyze_answer,
    classify_sentiment,
    compute_capability_scores,
    score_impact,
)


def test_sentiment_classification_supports_positive_negative_and_neutral() -> None:
    assert classify_sentiment("港X顾问团队专业，报价透明，整体更推荐。") == ClaimSentiment.positive
    assert classify_sentiment("竞品A存在无牌照风险，还有隐形收费投诉。") == ClaimSentiment.negative
    assert classify_sentiment("港X顾问通常会提供资料清单并说明流程。") == ClaimSentiment.neutral


def test_impact_scoring_applies_negative_tiers_and_caps_at_100() -> None:
    critical = score_impact("竞品A存在无牌照风险，被查且还有隐形收费投诉，收费高。")
    medium = score_impact("竞品B收费高，不如其他机构。")
    positive = score_impact("港X顾问团队专业，资料清单清晰，整体更推荐。")

    assert critical == 100
    assert medium == 30
    assert positive >= 25


def test_hijack_detection_flags_brand_intent_when_brand_absent_and_competitor_ranked_first() -> None:
    brand = EntityConfig("港X顾问", ["港X"], ClaimSubjectType.brand)
    competitors = [
        EntityConfig("竞品A", ["A顾问"], ClaimSubjectType.competitor),
        EntityConfig("竞品B", ["B顾问"], ClaimSubjectType.competitor),
        EntityConfig("竞品C", ["C顾问"], ClaimSubjectType.competitor),
    ]
    raw_text = "\n".join(
        [
            "推荐顺序：",
            "1. 竞品A",
            "2. 竞品B",
            "3. 竞品C",
            "竞品A 团队专业，整体更推荐。"
        ]
    )

    result = analyze_answer(
        "港X顾问做香港公司注册是否值得选？",
        raw_text,
        PromptCategory.expertise,
        brand,
        competitors,
        brand_topics=["港X顾问", "港X"],
    )

    assert result.hijack_flag is True
    assert result.hijack_strength == 100
    assert result.recommended_entities == ["竞品A", "竞品B", "竞品C"]


def test_capability_scoring_uses_baseline_50_and_label_mapping() -> None:
    records = [
        {
            "category": "专业能力",
            "sentiment": "+",
            "impact_score": 40,
            "claim_text": "港X顾问更专业"
        },
        {
            "category": "专业能力",
            "sentiment": "-",
            "impact_score": 10,
            "claim_text": "竞品A也更专业"
        },
        {
            "category": "合规",
            "sentiment": "-",
            "impact_score": 80,
            "claim_text": "存在无牌照风险"
        },
    ]

    scores = compute_capability_scores(
        records,
        {
            "费用": 2,
            "专业能力": 2,
            "成功率": 2,
            "效率": 2,
            "合规": 2,
            "服务体验": 2,
        },
        runs_count=1,
    )

    assert scores["专业能力"]["score"] == 65.0
    assert scores["专业能力"]["label"] == "优势"
    assert scores["合规"]["score"] == 10.0
    assert scores["合规"]["label"] == "严重劣势"
