from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ClaimSubjectType, RunProvider, RunStatus
from app.models import Answer, Brand, Claim, Competitor, Hijack, MetricSnapshot, Organization, Prompt, Run
from app.services.analysis import AnalysisResult, EntityConfig, analyze_answer
from app.services.brand_scope import resolve_brand
from app.services.metrics import build_snapshot_payload
from app.services.project_factory import ensure_brand_project_assets
from app.services.providers import get_provider_client


def _entity_from_brand(brand: Brand) -> EntityConfig:
    return EntityConfig(name=brand.name, aliases=brand.aliases or [], subject_type=ClaimSubjectType.brand)


def _entity_from_competitor(competitor: Competitor) -> EntityConfig:
    return EntityConfig(
        name=competitor.name,
        aliases=competitor.aliases or [],
        subject_type=ClaimSubjectType.competitor,
    )


def _load_org_context(
    db: Session, org_id: int, brand_id: int | None
) -> tuple[Organization, Brand, list[Competitor], list[Prompt]]:
    organization = db.scalar(select(Organization).where(Organization.id == org_id))
    brand = resolve_brand(db, org_id, brand_id=brand_id)
    if organization and brand:
        ensure_brand_project_assets(db, org_id, brand)
        db.flush()
    competitors_stmt = select(Competitor).where(Competitor.org_id == org_id)
    if brand:
        competitors_stmt = competitors_stmt.where(Competitor.brand_id == brand.id)
    else:
        competitors_stmt = competitors_stmt.where(Competitor.id == -1)
    competitors = list(db.scalars(competitors_stmt.order_by(Competitor.id.asc())))
    prompts = list(
        db.scalars(
            select(Prompt)
            .where(
                Prompt.org_id == org_id,
                Prompt.brand_id == brand.id,
                Prompt.is_active.is_(True),
            )
            .order_by(Prompt.id.asc())
        )
    )
    if not organization or not brand or len(competitors) < 3 or not prompts:
        raise ValueError("Organization is missing required config for run execution")
    return organization, brand, competitors, prompts


def execute_run_for_provider(
    db: Session,
    org_id: int,
    provider: RunProvider,
    *,
    brand_id: int | None = None,
    use_real: bool = False,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
) -> Run:
    _, brand, competitors, prompts = _load_org_context(db, org_id, brand_id=brand_id)

    run = Run(
        org_id=org_id,
        brand_id=brand.id,
        provider=provider,
        status=RunStatus.running,
        started_at=started_at or datetime.now(timezone.utc),
    )
    db.add(run)
    db.flush()

    brand_entity = _entity_from_brand(brand)
    competitor_entities = [_entity_from_competitor(competitor) for competitor in competitors]
    provider_client = get_provider_client(provider, use_real=use_real)
    brand_topics = [brand.name, *(brand.aliases or [])][:6]

    try:
        for prompt in prompts:
            provider_answer = provider_client.generate_answer(prompt, brand, competitors)
            answer = Answer(
                run_id=run.id,
                prompt_id=prompt.id,
                provider=provider,
                raw_text=provider_answer.raw_text,
            )
            db.add(answer)
            db.flush()

            result: AnalysisResult = analyze_answer(
                prompt.text,
                provider_answer.raw_text,
                prompt.category,
                brand_entity,
                competitor_entities,
                brand_topics=brand_topics,
            )

            for claim in result.claims:
                db.add(
                    Claim(
                        answer_id=answer.id,
                        subject_type=claim.subject_type,
                        subject_name=claim.subject_name,
                        claim_text=claim.claim_text,
                        sentiment=claim.sentiment,
                        impact_score=claim.impact_score,
                        risk_level=claim.risk_level,
                        is_factual_assertion=claim.is_factual_assertion,
                        category=claim.category,
                    )
                )

            db.add(
                Hijack(
                    answer_id=answer.id,
                    prompt_id=prompt.id,
                    provider=provider,
                    hijack_flag=result.hijack_flag,
                    hijack_strength=result.hijack_strength,
                    recommended_entities=result.recommended_entities,
                )
            )

        run.status = RunStatus.completed
        run.finished_at = finished_at or (run.started_at + timedelta(minutes=3))
        db.flush()

        snapshot = MetricSnapshot(
            run_id=run.id,
            org_id=org_id,
            jsonb_payload=build_snapshot_payload(db, org_id, run),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(run)
        return run
    except Exception:
        run.status = RunStatus.failed
        run.finished_at = datetime.now(timezone.utc)
        db.add(run)
        db.commit()
        raise


def execute_run_request(
    db: Session, org_id: int, provider: str, *, brand_id: int | None = None, use_real: bool = False
) -> list[Run]:
    providers = list(RunProvider) if provider == "all" else [RunProvider(provider)]
    runs: list[Run] = []
    for target in providers:
        runs.append(execute_run_for_provider(db, org_id, target, brand_id=brand_id, use_real=use_real))
    return runs
