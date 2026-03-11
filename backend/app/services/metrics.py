from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import ClaimRiskLevel, ClaimSentiment, ClaimSubjectType, PromptCategory, RunStatus
from app.models import Answer, Brand, Claim, Competitor, Hijack, MetricSnapshot, Prompt, Run
from app.services.analysis import compute_capability_scores
from app.services.brand_scope import resolve_brand
from app.services.dimensions import resolve_dimension_profile
from app.services.provider_scope import (
    normalize_provider_selector,
    provider_enums_from_selector,
    provider_values_from_selector,
)


def _default_dimension_profile_row(category: str) -> dict[str, str]:
    return {"display_name": category, "definition": "用于评估该维度的综合表现"}


def get_runs_for_scope(
    db: Session, org_id: int, range_key: str, provider: str, brand_id: int | None = None
) -> list[Run]:
    provider_enum_list = provider_enums_from_selector(provider)
    stmt = select(Run).where(Run.org_id == org_id, Run.status == RunStatus.completed)
    if provider_enum_list:
        stmt = stmt.where(Run.provider.in_(provider_enum_list))
    if brand_id is not None:
        stmt = stmt.where(Run.brand_id == brand_id)
    stmt = stmt.order_by(Run.started_at.desc())

    if range_key == "last_run":
        latest = db.scalar(stmt.limit(1))
        return [latest] if latest else []

    days = 7 if range_key == "7d" else 30
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    return list(db.scalars(stmt.where(Run.started_at >= window_start)))


def get_runs_for_period(
    db: Session,
    org_id: int,
    period_start: datetime,
    period_end: datetime,
    provider: str = "all",
    brand_id: int | None = None,
) -> list[Run]:
    provider_enum_list = provider_enums_from_selector(provider)
    stmt = select(Run).where(
        Run.org_id == org_id,
        Run.status == RunStatus.completed,
        Run.started_at >= period_start,
        Run.started_at <= period_end,
    )
    if provider_enum_list:
        stmt = stmt.where(Run.provider.in_(provider_enum_list))
    if brand_id is not None:
        stmt = stmt.where(Run.brand_id == brand_id)
    stmt = stmt.order_by(Run.started_at.desc())
    return list(db.scalars(stmt))


def _fetch_claim_records(db: Session, run_ids: list[int]) -> list[dict[str, Any]]:
    if not run_ids:
        return []
    rows = db.execute(
        select(Claim, Answer, Prompt, Run)
        .join(Answer, Claim.answer_id == Answer.id)
        .join(Prompt, Answer.prompt_id == Prompt.id)
        .join(Run, Answer.run_id == Run.id)
        .where(Run.id.in_(run_ids))
        .order_by(Claim.created_at.desc())
    ).all()

    records: list[dict[str, Any]] = []
    for claim, answer, prompt, run in rows:
        records.append(
            {
                "id": claim.id,
                "created_at": claim.created_at,
                "provider": run.provider.value,
                "prompt_id": prompt.id,
                "prompt_text": prompt.text,
                "category": claim.category.value,
                "subject_type": claim.subject_type.value,
                "subject_name": claim.subject_name,
                "claim_text": claim.claim_text,
                "sentiment": claim.sentiment.value,
                "impact_score": claim.impact_score,
                "risk_level": claim.risk_level.value,
                "raw_text": answer.raw_text,
            }
        )
    return records


def _prompt_counts_by_category(
    db: Session, org_id: int, brand_id: int | None = None
) -> dict[str, int]:
    stmt = (
        select(Prompt.category, func.count(Prompt.id))
        .where(Prompt.org_id == org_id, Prompt.is_active.is_(True))
    )
    if brand_id is not None:
        stmt = stmt.where(Prompt.brand_id == brand_id)
    rows = db.execute(stmt.group_by(Prompt.category)).all()
    counts = {category.value: total for category, total in rows}
    for category in PromptCategory:
        counts.setdefault(category.value, 1)
    return counts


def _mention_metrics(db: Session, run_ids: list[int], brand: Brand, competitors: list[Competitor]) -> dict[str, float]:
    if not run_ids:
        return {
            "mention_rate": 0.0,
            "top3_rate": 0.0,
            "first_pick_rate": 0.0,
            "competitor_appearance_rate": 0.0,
        }

    answers = list(
        db.scalars(select(Answer).where(Answer.run_id.in_(run_ids)).order_by(Answer.id.asc()))
    )
    total = max(len(answers), 1)
    brand_terms = [brand.name, *brand.aliases]
    competitor_terms = [token for competitor in competitors for token in [competitor.name, *competitor.aliases]]

    mention_count = 0
    top3_count = 0
    first_pick_count = 0
    competitor_appearance = 0

    for answer in answers:
        text = answer.raw_text
        if any(term in text for term in brand_terms):
            mention_count += 1
        if f"1. {brand.name}" in text or f"1) {brand.name}" in text:
            first_pick_count += 1
        for rank in (1, 2, 3):
            if f"{rank}. {brand.name}" in text or f"{rank}) {brand.name}" in text:
                top3_count += 1
                break
        if any(term in text for term in competitor_terms):
            competitor_appearance += 1

    return {
        "mention_rate": round(mention_count / total * 100, 2),
        "top3_rate": round(top3_count / total * 100, 2),
        "first_pick_rate": round(first_pick_count / total * 100, 2),
        "competitor_appearance_rate": round(competitor_appearance / total * 100, 2),
    }


def build_snapshot_payload(db: Session, org_id: int, run: Run) -> dict[str, Any]:
    brand = resolve_brand(db, org_id, run.brand_id)
    competitors = list(
        db.scalars(
            select(Competitor)
            .where(Competitor.org_id == org_id, Competitor.brand_id == run.brand_id)
            .order_by(Competitor.id.asc())
        )
    )
    claim_records = _fetch_claim_records(db, [run.id])
    prompt_counts = _prompt_counts_by_category(db, org_id, run.brand_id)
    brand_claims = [record for record in claim_records if record["subject_type"] == ClaimSubjectType.brand.value]
    capability_map = compute_capability_scores(brand_claims, prompt_counts, 1)

    competitor_map: list[dict[str, Any]] = []
    for competitor in competitors:
        competitor_claims = [
            record for record in claim_records if record["subject_name"] == competitor.name
        ]
        scores = compute_capability_scores(competitor_claims, prompt_counts, 1)
        competitor_map.append(
            {
                "competitor_id": competitor.id,
                "competitor_name": competitor.name,
                "scores": scores,
            }
        )

    mention_metrics = _mention_metrics(db, [run.id], brand, competitors) if brand else {}
    risk_claim_count = sum(
        1
        for record in claim_records
        if record["risk_level"] in {ClaimRiskLevel.high.value, ClaimRiskLevel.critical.value}
        and record["sentiment"] == ClaimSentiment.negative.value
    )
    return {
        "run_id": run.id,
        "provider": run.provider.value,
        "brand_id": run.brand_id,
        "brand_name": brand.name if brand else None,
        "started_at": run.started_at.isoformat(),
        "kpis": {**mention_metrics, "risk_claim_count": risk_claim_count},
        "capabilities": capability_map,
        "competitors": competitor_map,
    }


def build_overview_metrics(
    db: Session, org_id: int, range_key: str, provider: str, brand_id: int | None = None
) -> dict[str, Any]:
    normalized_provider = normalize_provider_selector(provider)
    runs = get_runs_for_scope(db, org_id, range_key, normalized_provider, brand_id=brand_id)
    return build_overview_from_runs(
        db, org_id, runs, range_key=range_key, provider=normalized_provider, brand_id=brand_id
    )


def build_overview_from_runs(
    db: Session,
    org_id: int,
    runs: list[Run],
    *,
    range_key: str,
    provider: str,
    brand_id: int | None = None,
) -> dict[str, Any]:
    normalized_provider = normalize_provider_selector(provider)
    run_ids = [run.id for run in runs]
    inferred_brand_id = brand_id if brand_id is not None else (runs[0].brand_id if runs else None)
    brand = resolve_brand(db, org_id, inferred_brand_id)
    if brand:
        competitors = list(
            db.scalars(
                select(Competitor).where(
                    Competitor.org_id == org_id,
                    Competitor.brand_id == brand.id,
                )
            )
        )
    else:
        competitors = []
    claim_records = _fetch_claim_records(db, run_ids)

    kpis = _mention_metrics(db, run_ids, brand, competitors) if brand else {}
    risk_claim_count = sum(
        1
        for record in claim_records
        if record["risk_level"] in {ClaimRiskLevel.high.value, ClaimRiskLevel.critical.value}
        and record["sentiment"] == ClaimSentiment.negative.value
    )
    kpis["risk_claim_count"] = risk_claim_count

    trend_stmt = (
        select(MetricSnapshot)
        .join(Run, MetricSnapshot.run_id == Run.id)
        .where(MetricSnapshot.org_id == org_id)
        .order_by(MetricSnapshot.created_at.desc())
        .limit(12)
    )
    if inferred_brand_id is not None:
        trend_stmt = trend_stmt.where(Run.brand_id == inferred_brand_id)
    trend_rows = list(db.scalars(trend_stmt))
    if normalized_provider != "all":
        selected_providers = set(provider_values_from_selector(normalized_provider))
        trend_rows = [
            row for row in trend_rows if str(row.jsonb_payload.get("provider", "")).lower() in selected_providers
        ]

    trend = [
        {
            "run_id": row.run_id,
            "provider": row.jsonb_payload.get("provider"),
            "started_at": row.jsonb_payload.get("started_at"),
            "mention_rate": row.jsonb_payload.get("kpis", {}).get("mention_rate", 0),
            "risk_claim_count": row.jsonb_payload.get("kpis", {}).get("risk_claim_count", 0),
        }
        for row in list(reversed(trend_rows[:4]))
    ]
    return {
        "range": range_key,
        "provider": normalized_provider,
        "brand_id": brand.id if brand else None,
        "brand_name": brand.name if brand else None,
        "kpis": kpis,
        "trend": trend,
    }


def build_capabilities_metrics(
    db: Session, org_id: int, range_key: str, provider: str, brand_id: int | None = None
) -> dict[str, Any]:
    normalized_provider = normalize_provider_selector(provider)
    runs = get_runs_for_scope(db, org_id, range_key, normalized_provider, brand_id=brand_id)
    return build_capabilities_from_runs(
        db, org_id, runs, range_key=range_key, provider=normalized_provider, brand_id=brand_id
    )


def build_capabilities_from_runs(
    db: Session,
    org_id: int,
    runs: list[Run],
    *,
    range_key: str,
    provider: str,
    brand_id: int | None = None,
) -> dict[str, Any]:
    normalized_provider = normalize_provider_selector(provider)
    run_ids = [run.id for run in runs]
    claim_records = _fetch_claim_records(db, run_ids)
    prompt_counts = _prompt_counts_by_category(
        db, org_id, brand_id if brand_id is not None else (runs[0].brand_id if runs else None)
    )
    runs_count = max(len(runs), 1)
    brand_claims = [record for record in claim_records if record["subject_type"] == ClaimSubjectType.brand.value]
    capability_map = compute_capability_scores(brand_claims, prompt_counts, runs_count)
    brand = resolve_brand(db, org_id, brand_id if brand_id is not None else (runs[0].brand_id if runs else None))
    profile = resolve_dimension_profile(brand.project_context if brand else None)

    categories = []
    for category in PromptCategory:
        row = capability_map[category.value].copy()
        row.update(profile.get(category.value, _default_dimension_profile_row(category.value)))
        categories.append(row)
    radar = [
        {
            "category": category["category"],
            "display_name": category["display_name"],
            "品牌": category["score"],
        }
        for category in categories
    ]
    return {
        "range": range_key,
        "provider": normalized_provider,
        "brand_id": brand.id if brand else None,
        "brand_name": brand.name if brand else None,
        "radar": radar,
        "categories": categories,
    }


def build_competitor_metrics(
    db: Session,
    org_id: int,
    range_key: str,
    provider: str,
    competitor_id: int | None = None,
    brand_id: int | None = None,
) -> dict[str, Any]:
    normalized_provider = normalize_provider_selector(provider)
    runs = get_runs_for_scope(db, org_id, range_key, normalized_provider, brand_id=brand_id)
    run_ids = [run.id for run in runs]
    claim_records = _fetch_claim_records(db, run_ids)
    prompt_counts = _prompt_counts_by_category(
        db, org_id, brand_id if brand_id is not None else (runs[0].brand_id if runs else None)
    )
    runs_count = max(len(runs), 1)
    brand = resolve_brand(db, org_id, brand_id if brand_id is not None else (runs[0].brand_id if runs else None))
    if not brand:
        return {
            "competitor_id": competitor_id,
            "range": range_key,
            "provider": normalized_provider,
            "brand_id": None,
            "brand_name": None,
            "comparisons": [],
        }

    profile = resolve_dimension_profile(brand.project_context)
    competitors_query = select(Competitor).where(
        Competitor.org_id == org_id, Competitor.brand_id == brand.id
    )
    if competitor_id:
        competitors_query = competitors_query.where(Competitor.id == competitor_id)
    competitors = list(db.scalars(competitors_query.order_by(Competitor.id.asc())))

    comparisons: list[dict[str, Any]] = []
    for competitor in competitors:
        competitor_claims = [
            record for record in claim_records if record["subject_name"] == competitor.name
        ]
        score_map = compute_capability_scores(competitor_claims, prompt_counts, runs_count)
        rows = []
        for category in PromptCategory:
            row = score_map[category.value].copy()
            row.update(profile.get(category.value, _default_dimension_profile_row(category.value)))
            rows.append(row)
        comparisons.append(
            {
                "competitor_id": competitor.id,
                "competitor_name": competitor.name,
                "scores": rows,
            }
        )

    return {
        "competitor_id": competitor_id,
        "range": range_key,
        "provider": normalized_provider,
        "brand_id": brand.id,
        "brand_name": brand.name,
        "comparisons": comparisons,
    }


def build_dimension_audit(
    db: Session,
    org_id: int,
    *,
    brand_id: int | None = None,
) -> dict[str, Any]:
    brand = resolve_brand(db, org_id, brand_id=brand_id)
    profile = resolve_dimension_profile(brand.project_context if brand else None)
    capability_payload = build_capabilities_metrics(
        db,
        org_id,
        range_key="last_run",
        provider="all",
        brand_id=brand.id if brand else brand_id,
    )
    page_categories = {
        str(item.get("category", "")): item
        for item in capability_payload.get("categories", [])
        if isinstance(item, dict)
    }

    rows: list[dict[str, Any]] = []
    for category in PromptCategory:
        category_key = category.value
        contract_row = profile.get(category_key, _default_dimension_profile_row(category_key))
        page_row = page_categories.get(category_key, {})
        page_display_name = str(page_row.get("display_name", ""))
        page_definition = str(page_row.get("definition", ""))
        expected_display_name = str(contract_row.get("display_name", category_key))
        expected_definition = str(contract_row.get("definition", "用于评估该维度的综合表现"))
        is_consistent = (
            page_display_name == expected_display_name
            and page_definition == expected_definition
        )
        rows.append(
            {
                "category": category_key,
                "data_source_dimension": expected_display_name,
                "page_dimension": page_display_name or "缺失",
                "report_dimension": expected_display_name,
                "expected_definition": expected_definition,
                "page_definition": page_definition or "缺失",
                "is_consistent": is_consistent,
            }
        )

    mismatches = [item["category"] for item in rows if not item["is_consistent"]]
    return {
        "brand_id": brand.id if brand else None,
        "brand_name": brand.name if brand else None,
        "project_context": brand.project_context if brand else None,
        "overall_consistent": len(mismatches) == 0,
        "mismatch_categories": mismatches,
        "rows": rows,
    }


def build_projects_overview(db: Session, org_id: int) -> dict[str, Any]:
    brands = list(
        db.scalars(select(Brand).where(Brand.org_id == org_id).order_by(Brand.id.asc()))
    )
    if not brands:
        return {"total_projects": 0, "healthy_projects": 0, "warning_projects": 0, "items": []}

    window_start = datetime.now(timezone.utc) - timedelta(days=30)
    items: list[dict[str, Any]] = []
    healthy = 0
    warning = 0

    for brand in brands:
        competitor_count = int(
            db.scalar(
                select(func.count(Competitor.id)).where(
                    Competitor.org_id == org_id, Competitor.brand_id == brand.id
                )
            )
            or 0
        )
        active_prompt_count = int(
            db.scalar(
                select(func.count(Prompt.id)).where(
                    Prompt.org_id == org_id, Prompt.brand_id == brand.id, Prompt.is_active.is_(True)
                )
            )
            or 0
        )
        run_count_30d = int(
            db.scalar(
                select(func.count(Run.id)).where(
                    Run.org_id == org_id,
                    Run.brand_id == brand.id,
                    Run.started_at >= window_start,
                )
            )
            or 0
        )
        high_risk_claim_count_30d = int(
            db.scalar(
                select(func.count(Claim.id))
                .join(Answer, Claim.answer_id == Answer.id)
                .join(Run, Answer.run_id == Run.id)
                .where(
                    Run.org_id == org_id,
                    Run.brand_id == brand.id,
                    Run.started_at >= window_start,
                    Claim.risk_level.in_([ClaimRiskLevel.high, ClaimRiskLevel.critical]),
                    Claim.sentiment == ClaimSentiment.negative,
                )
            )
            or 0
        )
        hijack_count_30d = int(
            db.scalar(
                select(func.count(Hijack.id))
                .join(Answer, Hijack.answer_id == Answer.id)
                .join(Run, Answer.run_id == Run.id)
                .where(
                    Run.org_id == org_id,
                    Run.brand_id == brand.id,
                    Run.started_at >= window_start,
                    Hijack.hijack_flag.is_(True),
                )
            )
            or 0
        )
        last_run = db.scalar(
            select(Run)
            .where(Run.org_id == org_id, Run.brand_id == brand.id)
            .order_by(Run.started_at.desc())
            .limit(1)
        )
        mention_rate_last_run = 0.0
        if last_run:
            snapshot = db.scalar(
                select(MetricSnapshot)
                .where(MetricSnapshot.run_id == last_run.id)
                .order_by(MetricSnapshot.created_at.desc())
                .limit(1)
            )
            if snapshot:
                mention_rate_last_run = float(snapshot.jsonb_payload.get("kpis", {}).get("mention_rate", 0))

        is_warning = (
            run_count_30d == 0
            or high_risk_claim_count_30d >= 80
            or hijack_count_30d >= 40
            or (last_run is not None and last_run.status != RunStatus.completed)
        )
        if is_warning:
            warning += 1
        else:
            healthy += 1

        items.append(
            {
                "brand_id": brand.id,
                "brand_name": brand.name,
                "project_context": brand.project_context,
                "competitor_count": competitor_count,
                "active_prompt_count": active_prompt_count,
                "run_count_30d": run_count_30d,
                "high_risk_claim_count_30d": high_risk_claim_count_30d,
                "hijack_count_30d": hijack_count_30d,
                "mention_rate_last_run": round(mention_rate_last_run, 2),
                "last_run_provider": last_run.provider if last_run else None,
                "last_run_status": last_run.status if last_run else None,
                "last_run_started_at": last_run.started_at if last_run else None,
            }
        )

    items.sort(
        key=lambda item: (
            item["last_run_started_at"] is None,
            item["last_run_started_at"] or datetime(1970, 1, 1, tzinfo=timezone.utc),
        ),
        reverse=True,
    )
    return {
        "total_projects": len(items),
        "healthy_projects": healthy,
        "warning_projects": warning,
        "items": items,
    }


def list_claims(
    db: Session,
    org_id: int,
    provider: str = "all",
    category: str | None = None,
    risk_level: str | None = None,
    subject_type: str | None = None,
    search: str | None = None,
    limit: int = 200,
    brand_id: int | None = None,
) -> list[dict[str, Any]]:
    normalized_provider = normalize_provider_selector(provider)
    stmt = (
        select(Claim, Answer, Prompt, Run)
        .join(Answer, Claim.answer_id == Answer.id)
        .join(Prompt, Answer.prompt_id == Prompt.id)
        .join(Run, Answer.run_id == Run.id)
        .where(Run.org_id == org_id)
    )
    provider_enum_list = provider_enums_from_selector(normalized_provider)
    if provider_enum_list:
        stmt = stmt.where(Run.provider.in_(provider_enum_list))
    if brand_id is not None:
        stmt = stmt.where(Run.brand_id == brand_id)
    if category:
        stmt = stmt.where(Claim.category == PromptCategory(category))
    if risk_level:
        stmt = stmt.where(Claim.risk_level == ClaimRiskLevel(risk_level))
    if subject_type:
        stmt = stmt.where(Claim.subject_type == ClaimSubjectType(subject_type))
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            Claim.claim_text.ilike(pattern) | Prompt.text.ilike(pattern) | Claim.subject_name.ilike(pattern)
        )

    rows = db.execute(stmt.order_by(Claim.created_at.desc()).limit(min(limit, 500))).all()
    results: list[dict[str, Any]] = []
    for claim, answer, prompt, run in rows:
        results.append(
            {
                "id": claim.id,
                "created_at": claim.created_at,
                "provider": run.provider,
                "prompt_id": prompt.id,
                "prompt_text": prompt.text,
                "category": claim.category,
                "subject_type": claim.subject_type,
                "subject_name": claim.subject_name,
                "claim_text": claim.claim_text,
                "sentiment": claim.sentiment,
                "impact_score": claim.impact_score,
                "risk_level": claim.risk_level,
                "raw_text": answer.raw_text,
            }
        )
    return results


def get_claim_detail(
    db: Session, org_id: int, claim_id: int, brand_id: int | None = None
) -> dict[str, Any] | None:
    stmt = (
        select(Claim, Answer, Prompt, Run)
        .join(Answer, Claim.answer_id == Answer.id)
        .join(Prompt, Answer.prompt_id == Prompt.id)
        .join(Run, Answer.run_id == Run.id)
        .where(Claim.id == claim_id, Run.org_id == org_id)
    )
    if brand_id is not None:
        stmt = stmt.where(Run.brand_id == brand_id)
    row = db.execute(stmt).first()
    if not row:
        return None
    claim, answer, prompt, run = row
    return {
        "id": claim.id,
        "created_at": claim.created_at,
        "provider": run.provider,
        "prompt_id": prompt.id,
        "prompt_text": prompt.text,
        "category": claim.category,
        "subject_type": claim.subject_type,
        "subject_name": claim.subject_name,
        "claim_text": claim.claim_text,
        "sentiment": claim.sentiment,
        "impact_score": claim.impact_score,
        "risk_level": claim.risk_level,
        "raw_text": answer.raw_text,
    }


def list_claims_by_run_ids(db: Session, run_ids: list[int]) -> list[dict[str, Any]]:
    return _fetch_claim_records(db, run_ids)


def list_hijacks(
    db: Session, org_id: int, range_key: str, provider: str, brand_id: int | None = None
) -> dict[str, Any]:
    normalized_provider = normalize_provider_selector(provider)
    runs = get_runs_for_scope(db, org_id, range_key, normalized_provider, brand_id=brand_id)
    return list_hijacks_by_run_ids(db, org_id, [run.id for run in runs], brand_id=brand_id)


def list_hijacks_by_run_ids(
    db: Session, org_id: int, run_ids: list[int], brand_id: int | None = None
) -> dict[str, Any]:
    if not run_ids:
        return {"items": [], "top_prompts": []}
    rows = db.execute(
        select(Hijack, Answer, Prompt, Run)
        .join(Answer, Hijack.answer_id == Answer.id)
        .join(Prompt, Hijack.prompt_id == Prompt.id)
        .join(Run, Answer.run_id == Run.id)
        .where(Run.id.in_(run_ids))
        .order_by(Hijack.hijack_strength.desc(), Hijack.created_at.desc())
    ).all()

    items: list[dict[str, Any]] = []
    counter: Counter[str] = Counter()
    brand_terms = _brand_terms(db, org_id, brand_id)
    for hijack, answer, prompt, run in rows:
        items.append(
            {
                "id": hijack.id,
                "created_at": hijack.created_at,
                "provider": run.provider.value,
                "prompt_id": prompt.id,
                "prompt_text": prompt.text,
                "hijack_flag": hijack.hijack_flag,
                "hijack_strength": hijack.hijack_strength,
                "recommended_entities": hijack.recommended_entities,
                "brand_present": any(term in answer.raw_text for term in brand_terms),
            }
        )
        if hijack.hijack_flag:
            counter[prompt.text] += 1

    top_prompts = [
        {"prompt_text": prompt_text, "count": count}
        for prompt_text, count in counter.most_common(8)
    ]
    return {"items": items, "top_prompts": top_prompts}


def _brand_terms(db: Session, org_id: int, brand_id: int | None = None) -> list[str]:
    brand = resolve_brand(db, org_id, brand_id=brand_id)
    if not brand:
        return []
    return [brand.name, *brand.aliases]
