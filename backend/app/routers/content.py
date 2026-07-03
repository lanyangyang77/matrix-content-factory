"""FastAPI router for content generation endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.services.langchain_service import generate_content
from app.database import get_db
from app.models.pydantic_models import (
    APIResponse,
    ContentGenerateRequest,
    ContentGenerateResult,
    ContentTaskStatusResponse,
)
from app.models.sqlalchemy_models import ContentPackage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/content", tags=["content"])


def _resolve_tenant_id(x_tenant_id: str | None = None) -> str:
    return x_tenant_id or "dev-default-tenant"


@router.post("/generate", response_model=APIResponse)
async def create_generation_task(
    request: ContentGenerateRequest,
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID"),
    db: Session = Depends(get_db),
):
    """Directly call LLM, bypassing Celery entirely."""
    from app.services.langchain_service import generate_content

    tenant_id = _resolve_tenant_id(x_tenant_id)

    try:
        result = await generate_content(
            industry=request.industry,
            style=request.style,
            platforms=request.platforms,
        )

        pkg = ContentPackage(
            tenant_id=tenant_id,
            industry=request.industry,
            style=request.style,
            platforms=request.platforms,
            status="completed",
            merchant_id=request.merchant_id,
            result=result.model_dump(),
        )
        db.add(pkg)
        db.commit()
        db.refresh(pkg)

        logger.info("Generated content for industry=%s (package=%s)", request.industry, pkg.id)
        return APIResponse(
            success=True,
            data=ContentTaskStatusResponse(
                task_id=pkg.id,
                package_id=pkg.id,
                status="completed",
                result=result,
            ),
        )

    except Exception as exc:
        logger.error("Content generation failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")


@router.get("/task/{task_id}", response_model=APIResponse)
async def get_generation_task_status(
    task_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve a previously saved content package by id."""
    pkg = db.query(ContentPackage).filter(ContentPackage.id == task_id).first()
    if pkg is None:
        raise HTTPException(status_code=404, detail=f"Package {task_id} not found.")

    result: ContentGenerateResult | None = None
    if pkg.result:
        result = ContentGenerateResult(**pkg.result)

    return APIResponse(
        success=True,
        data=ContentTaskStatusResponse(
            task_id=task_id,
            package_id=task_id,
            status=pkg.status,
            result=result,
            error=pkg.error_message,
        ).model_dump(mode="json"),
    )
    from app.services.langchain_service import generate_content, get_llm
