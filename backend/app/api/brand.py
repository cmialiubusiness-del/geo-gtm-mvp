from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Brand, User
from app.schemas import BrandBase, BrandCreate, BrandResponse
from app.services.brand_scope import list_org_brands, resolve_brand
from app.services.project_factory import (
    ensure_brand_project_assets,
    find_existing_brand,
    infer_project_context,
    merge_duplicate_brands,
    normalize_brand_aliases,
)

router = APIRouter(tags=["brand"])


@router.get("/brand", response_model=BrandResponse)
def get_brand(
    brand_id: int | None = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> BrandResponse:
    if merge_duplicate_brands(db, current_user.org_id):
        db.commit()
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")
    ensure_brand_project_assets(db, current_user.org_id, brand)
    db.commit()
    db.refresh(brand)
    return BrandResponse.model_validate(brand).model_copy(update={"project_exists": False})


@router.get("/brands", response_model=list[BrandResponse])
def get_brands(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[BrandResponse]:
    if merge_duplicate_brands(db, current_user.org_id):
        db.commit()
    brands = list_org_brands(db, current_user.org_id)
    for brand in brands:
        ensure_brand_project_assets(db, current_user.org_id, brand)
    db.commit()
    for brand in brands:
        db.refresh(brand)
    return [BrandResponse.model_validate(item).model_copy(update={"project_exists": False}) for item in brands]


@router.post("/brands", response_model=BrandResponse)
def create_brand(
    payload: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BrandResponse:
    if merge_duplicate_brands(db, current_user.org_id):
        db.commit()
    aliases = normalize_brand_aliases(payload.name, payload.aliases)
    inferred_context = infer_project_context(payload.name, payload.project_context, aliases)
    existing = find_existing_brand(db, current_user.org_id, payload.name, aliases)
    if existing:
        merged_aliases = normalize_brand_aliases(
            existing.name,
            [*(existing.aliases or []), payload.name, *aliases],
        )
        existing.aliases = merged_aliases
        existing.project_context = infer_project_context(
            existing.name,
            existing.project_context if existing.project_context != "通用行业" else inferred_context,
            merged_aliases,
        )
        ensure_brand_project_assets(db, current_user.org_id, existing)
        db.commit()
        db.refresh(existing)
        return BrandResponse.model_validate(existing).model_copy(update={"project_exists": True})

    brand = Brand(
        org_id=current_user.org_id,
        name=payload.name,
        aliases=aliases,
        project_context=inferred_context,
    )
    db.add(brand)
    db.flush()
    ensure_brand_project_assets(db, current_user.org_id, brand)
    db.commit()
    db.refresh(brand)
    return BrandResponse.model_validate(brand).model_copy(update={"project_exists": False})


@router.put("/brand", response_model=BrandResponse)
def upsert_brand(
    payload: BrandBase,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BrandResponse:
    if merge_duplicate_brands(db, current_user.org_id):
        db.commit()
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if brand_id is not None and not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")

    aliases = normalize_brand_aliases(payload.name, payload.aliases)
    inferred_context = infer_project_context(payload.name, payload.project_context, aliases)
    existing = find_existing_brand(db, current_user.org_id, payload.name, aliases)

    if existing and (not brand or existing.id != brand.id):
        if brand and brand.id != existing.id:
            brand.name = payload.name
            brand.aliases = aliases
            brand.project_context = inferred_context
            merge_duplicate_brands(db, current_user.org_id)
        merged_aliases = normalize_brand_aliases(
            existing.name,
            [*(existing.aliases or []), payload.name, *aliases],
        )
        existing.aliases = merged_aliases
        existing.project_context = infer_project_context(
            existing.name,
            existing.project_context if existing.project_context != "通用行业" else inferred_context,
            merged_aliases,
        )
        ensure_brand_project_assets(db, current_user.org_id, existing)
        db.commit()
        db.refresh(existing)
        return BrandResponse.model_validate(existing).model_copy(update={"project_exists": True})

    if brand:
        brand.name = payload.name
        brand.aliases = aliases
        brand.project_context = inferred_context
    else:
        brand = Brand(
            org_id=current_user.org_id,
            name=payload.name,
            aliases=aliases,
            project_context=inferred_context,
        )
        db.add(brand)
        db.flush()
    ensure_brand_project_assets(db, current_user.org_id, brand)
    merge_duplicate_brands(db, current_user.org_id)
    db.commit()
    resolved = resolve_brand(db, current_user.org_id, brand_id=brand.id)
    if not resolved:
        resolved = find_existing_brand(db, current_user.org_id, payload.name, aliases)
    if not resolved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")
    db.refresh(resolved)
    return BrandResponse.model_validate(resolved).model_copy(update={"project_exists": False})
