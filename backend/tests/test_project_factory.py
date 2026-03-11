from app.services.project_factory import (
    CUSTOM_INDUSTRY,
    brand_identity_tokens,
    generate_competitor_profiles,
    generate_project_prompts,
    infer_project_context,
    industry_options,
    normalize_brand_aliases,
    normalize_project_context,
    recommend_real_competitors,
    search_real_competitors,
)


def test_generate_project_prompts_builds_50_brand_scoped_questions() -> None:
    prompts = generate_project_prompts("比亚迪", "新能源车")
    assert len(prompts) == 50
    assert all("比亚迪" in item["text"] for item in prompts)
    assert any("新能源车" in item["text"] for item in prompts)


def test_generate_competitor_profiles_returns_three_unique_names() -> None:
    profiles = generate_competitor_profiles("比亚迪", "新能源车")
    names = [item[0] for item in profiles]
    assert len(names) == 3
    assert len(set(names)) == 3
    assert all("比亚迪" not in name for name in names)


def test_recommend_real_competitors_uses_industry_catalog() -> None:
    candidates = recommend_real_competitors("比亚迪", "新能源车", limit=5)
    names = [item["name"] for item in candidates]
    assert any(name in {"特斯拉", "蔚来", "小鹏汽车", "理想汽车"} for name in names)


def test_industry_options_contains_custom_option() -> None:
    assert CUSTOM_INDUSTRY in industry_options()


def test_infer_project_context_can_guess_from_brand_name() -> None:
    assert infer_project_context("比亚迪", "通用行业") == "新能源车"


def test_infer_project_context_supports_english_alias_for_same_brand() -> None:
    assert infer_project_context("BYD", "通用行业", aliases=["比亚迪"]) == "新能源车"


def test_normalize_project_context_maps_legacy_labels_to_standard_labels() -> None:
    assert normalize_project_context("香港跨境服务") == "跨境贸易与服务"
    assert normalize_project_context("医疗健康") == "医疗器械"


def test_infer_project_context_normalizes_legacy_industry_label() -> None:
    assert infer_project_context("医疗品牌Z", "医疗健康") == "医疗器械"


def test_search_real_competitors_matches_query() -> None:
    results = search_real_competitors("比亚迪", query="特斯拉", project_context="新能源车", limit=5)
    names = [item["name"] for item in results]
    assert "特斯拉" in names


def test_recommend_real_competitors_for_marketing_service() -> None:
    results = recommend_real_competitors("云上科技", "营销服务", limit=5)
    names = [item["name"] for item in results]
    assert any(name in {"蓝色光标", "省广集团", "华扬联众"} for name in names)


def test_normalize_brand_aliases_bridges_byd_and_chinese_name() -> None:
    aliases = normalize_brand_aliases("BYD", ["比亚迪", "byd"])
    lowered = {item.lower() for item in aliases}
    assert "比亚迪" in aliases
    assert "byd" not in lowered


def test_brand_identity_tokens_treats_byd_and_chinese_as_same_identity() -> None:
    tokens = brand_identity_tokens("BYD", ["比亚迪"])
    assert "byd" in tokens
    assert "比亚迪" in tokens
