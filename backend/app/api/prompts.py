from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Prompt, User
from app.schemas import PromptBase, PromptResponse
from app.services.brand_scope import resolve_brand
from app.services.project_factory import ensure_brand_project_assets

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("", response_model=list[PromptResponse])
def list_prompts(
    brand_id: int | None = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[PromptResponse]:
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        return []
    ensure_brand_project_assets(db, current_user.org_id, brand)
    db.commit()
    stmt = select(Prompt).where(Prompt.org_id == current_user.org_id, Prompt.brand_id == brand.id)
    if not include_inactive:
        stmt = stmt.where(Prompt.is_active.is_(True))
    prompts = list(db.scalars(stmt.order_by(Prompt.id.asc())))
    return [PromptResponse.model_validate(item) for item in prompts]


@router.post("", response_model=PromptResponse)
def create_prompt(
    payload: PromptBase,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptResponse:
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")
    prompt = Prompt(org_id=current_user.org_id, brand_id=brand.id, **payload.model_dump())
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return PromptResponse.model_validate(prompt)


@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(
    prompt_id: int,
    payload: PromptBase,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptResponse:
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")
    prompt = db.scalar(
        select(Prompt).where(
            Prompt.id == prompt_id,
            Prompt.org_id == current_user.org_id,
            Prompt.brand_id == brand.id,
        )
    )
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
    for field, value in payload.model_dump().items():
        setattr(prompt, field, value)
    db.commit()
    db.refresh(prompt)
    return PromptResponse.model_validate(prompt)


@router.delete("/{prompt_id}")
def delete_prompt(
    prompt_id: int,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")
    prompt = db.scalar(
        select(Prompt).where(
            Prompt.id == prompt_id,
            Prompt.org_id == current_user.org_id,
            Prompt.brand_id == brand.id,
        )
    )
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
    db.delete(prompt)
    db.commit()
    return {"status": "deleted"}
