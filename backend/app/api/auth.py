from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import create_access_token, get_password_hash, verify_password
from app.deps import get_current_user, get_db
from app.models import Brand, Organization, User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.project_factory import ensure_brand_project_assets, infer_project_context, normalize_brand_aliases

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在")

    org = Organization(name=payload.organization_name)
    db.add(org)
    db.flush()
    user = User(
        org_id=org.id,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=UserRole.admin,
    )
    db.add(user)
    default_brand_name = payload.brand_name or f"{payload.organization_name}主品牌"
    default_aliases = normalize_brand_aliases(default_brand_name, [])
    brand = Brand(
        org_id=org.id,
        name=default_brand_name,
        aliases=default_aliases,
        project_context=infer_project_context(default_brand_name, payload.brand_context, default_aliases),
    )
    db.add(brand)
    db.flush()
    ensure_brand_project_assets(db, org.id, brand)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        org_id=current_user.org_id,
        organization_name=current_user.organization.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
    )
