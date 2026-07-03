"""FastAPI router for merchant profile management.

Endpoints:
  CRUD for merchant_profiles
  GET merchant content history
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pydantic_models import (
    APIResponse,
    ContentGenerateResult,
    ContentHistoryItem,
    MerchantCreate,
    MerchantListResponse,
    MerchantResponse,
    MerchantUpdate,
)
from app.models.sqlalchemy_models import ContentPackage, MerchantProfile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/merchants", tags=["merchants"])


def _resolve_tenant_id(x_tenant_id: str | None = None) -> str:
    return x_tenant_id or "dev-default-tenant"


@router.get("", response_model=APIResponse)
async def list_merchants(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID"),
    db: Session = Depends(get_db),
):
    """获取所有商家档案列表"""
    tenant_id = _resolve_tenant_id(x_tenant_id)
    merchants = (
        db.query(MerchantProfile)
        .filter(MerchantProfile.tenant_id == tenant_id)
        .order_by(MerchantProfile.created_at.desc())
        .all()
    )
    result = []
    for m in merchants:
        count = db.query(ContentPackage).filter(ContentPackage.merchant_id == m.id).count()
        result.append(MerchantListResponse(
            id=m.id,
            merchant_name=m.merchant_name,
            industry=m.industry,
            is_active=m.is_active,
            content_count=count,
            created_at=m.created_at,
        ))
    return APIResponse(success=True, data=[r.model_dump(mode="json") for r in result])


@router.post("", response_model=APIResponse)
async def create_merchant(
    request: MerchantCreate,
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID"),
    db: Session = Depends(get_db),
):
    """创建新的商家档案"""
    tenant_id = _resolve_tenant_id(x_tenant_id)
    merchant = MerchantProfile(
        tenant_id=tenant_id,
        merchant_name=request.merchant_name,
        industry=request.industry,
        target_audience=request.target_audience,
        notes=request.notes,
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    logger.info("Created merchant %s (%s)", merchant.id, merchant.merchant_name)
    data = MerchantResponse(
        id=merchant.id,
        tenant_id=merchant.tenant_id,
        merchant_name=merchant.merchant_name,
        industry=merchant.industry,
        target_audience=merchant.target_audience,
        notes=merchant.notes,
        is_active=merchant.is_active,
        created_at=merchant.created_at,
        updated_at=merchant.updated_at,
    )
    return APIResponse(success=True, data=data.model_dump(mode="json"))


@router.get("/{merchant_id}", response_model=APIResponse)
async def get_merchant(
    merchant_id: str,
    db: Session = Depends(get_db),
):
    """获取单个商家档案详情"""
    merchant = db.query(MerchantProfile).filter(MerchantProfile.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    count = db.query(ContentPackage).filter(ContentPackage.merchant_id == merchant_id).count()
    data = MerchantResponse(
        id=merchant.id,
        tenant_id=merchant.tenant_id,
        merchant_name=merchant.merchant_name,
        industry=merchant.industry,
        target_audience=merchant.target_audience,
        notes=merchant.notes,
        is_active=merchant.is_active,
        content_count=count,
        created_at=merchant.created_at,
        updated_at=merchant.updated_at,
    )
    return APIResponse(success=True, data=data.model_dump(mode="json"))


@router.put("/{merchant_id}", response_model=APIResponse)
async def update_merchant(
    merchant_id: str,
    request: MerchantUpdate,
    db: Session = Depends(get_db),
):
    """更新商家档案信息"""
    merchant = db.query(MerchantProfile).filter(MerchantProfile.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(merchant, key, value)
    db.commit()
    db.refresh(merchant)
    return APIResponse(success=True, message="商家信息已更新")


@router.delete("/{merchant_id}", response_model=APIResponse)
async def delete_merchant(
    merchant_id: str,
    db: Session = Depends(get_db),
):
    """删除商家档案"""
    merchant = db.query(MerchantProfile).filter(MerchantProfile.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    db.delete(merchant)
    db.commit()
    return APIResponse(success=True, message="商家已删除")


@router.get("/{merchant_id}/history", response_model=APIResponse)
async def get_merchant_content_history(
    merchant_id: str,
    db: Session = Depends(get_db),
):
    """获取某个商家的所有历史生成内容"""
    merchant = db.query(MerchantProfile).filter(MerchantProfile.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    packages = (
        db.query(ContentPackage)
        .filter(ContentPackage.merchant_id == merchant_id)
        .order_by(ContentPackage.created_at.desc())
        .all()
    )
    items = []
    for pkg in packages:
        result_obj = None
        if pkg.result:
            try:
                result_obj = ContentGenerateResult(**pkg.result)
            except Exception:
                pass
        items.append(ContentHistoryItem(
            id=pkg.id,
            merchant_id=pkg.merchant_id,
            industry=pkg.industry,
            style=pkg.style,
            platforms=pkg.platforms,
            status=pkg.status,
            result=result_obj,
            created_at=pkg.created_at,
        ))
    return APIResponse(success=True, data=[i.model_dump(mode="json") for i in items])
