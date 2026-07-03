"""Pydantic schemas for request/response validation and structured LLM output."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Content Package schemas
# ---------------------------------------------------------------------------


class ContentGenerateRequest(BaseModel):
    """Request body for POST /api/v1/content/generate."""
    industry: str = Field(..., min_length=1, max_length=255, description="Target industry, e.g. 'New energy vehicles'")
    style: str = Field(..., min_length=1, max_length=255, description="Content style, e.g. 'Professional' or 'Humorous'")
    platforms: list[str] = Field(..., min_length=1, description="Target platforms, e.g. ['Douyin', 'Xiaohongshu']")
    merchant_id: Optional[str] = Field(None, description="关联商家ID（可选）")


class ContentTaskResponse(BaseModel):
    """Immediate response returned when a generation task is accepted."""
    task_id: str = Field(..., description="Celery task ID for polling")
    status: str = Field(default="pending", description="Current status")
    package_id: Optional[str] = None
    message: str = Field(default="Task accepted and queued for processing.")


class ViralAngle(BaseModel):
    """A single viral content angle generated in Stage 1."""
    title: str = Field(..., description="Catchy title for the angle")
    hook: str = Field(..., description="Opening hook sentence")
    angle_description: str = Field(..., description="Brief explanation of why this angle works")


class AnglesOutput(BaseModel):
    """Wrapper schema for structured output of Stage 1."""
    angles: list[ViralAngle] = Field(..., description="List of 3 viral content angles")


class PlatformPost(BaseModel):
    """A platform-specific generated post from Stage 2."""
    platform: str = Field(..., description="Target platform name")
    title: str = Field(..., description="Post title / headline")
    body: str = Field(..., description="Main post body / script")
    tags: list[str] = Field(default_factory=list, description="Hashtag suggestions")
    visual_suggestion: str = Field(default="", description="Image / visual concept prompt")


class PostsOutput(BaseModel):
    """Wrapper schema for structured output of Stage 2."""
    posts: list[PlatformPost] = Field(..., description="List of platform-specific posts")


class ContentGenerateResult(BaseModel):
    """Final structured output of the multi-stage prompt chain."""
    industry: str
    style: str
    platforms: list[str]
    angles: list[ViralAngle] = Field(default_factory=list)
    posts: list[PlatformPost] = Field(default_factory=list)


class ContentTaskStatusResponse(BaseModel):
    """Polling response for GET /api/v1/content/task/<id>."""
    task_id: str
    status: str
    package_id: Optional[str] = None
    result: Optional[ContentGenerateResult] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# CRM Lead schemas
# ---------------------------------------------------------------------------


class CRMLeadCreate(BaseModel):
    """Request body for creating a new CRM lead."""
    name: str = Field(..., min_length=1, max_length=255)
    contact_info: Optional[dict[str, Any]] = None
    source_channel: Optional[str] = None
    notes: Optional[str] = None


class CRMLeadUpdate(BaseModel):
    """Request body for updating an existing CRM lead."""
    name: Optional[str] = None
    contact_info: Optional[dict[str, Any]] = None
    source_channel: Optional[str] = None
    ai_tags: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    score: Optional[float] = None
    interaction_history: Optional[dict[str, Any]] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class CRMLeadResponse(BaseModel):
    """CRM lead returned to the frontend."""
    id: str
    tenant_id: str
    name: str
    contact_info: Optional[dict[str, Any]] = None
    source_channel: Optional[str] = None
    ai_tags: Optional[dict[str, Any]] = None
    status: str
    score: float
    interaction_history: Optional[dict[str, Any]] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Generic API wrappers
# ---------------------------------------------------------------------------


class APIResponse(BaseModel):
    """Standard API envelope."""
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error envelope."""
    success: bool = False
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."
    details: Optional[Any] = None


# ---------------------------------------------------------------------------
# Merchant Profile schemas
# ---------------------------------------------------------------------------


class MerchantCreate(BaseModel):
    """Request body for creating a merchant profile."""
    merchant_name: str = Field(..., min_length=1, max_length=255, description="商家名称")
    industry: str = Field(..., min_length=1, max_length=255, description="所属行业")
    target_audience: Optional[str] = Field(None, description="目标客户群体描述")
    notes: Optional[str] = Field(None, description="备注信息")


class MerchantUpdate(BaseModel):
    """Request body for updating a merchant profile."""
    merchant_name: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class MerchantResponse(BaseModel):
    """Merchant profile returned to the frontend."""
    id: str
    tenant_id: str
    merchant_name: str
    industry: str
    target_audience: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    content_count: int = 0

    model_config = {"from_attributes": True}


class MerchantListResponse(BaseModel):
    """Lightweight merchant list item."""
    id: str
    merchant_name: str
    industry: str
    is_active: bool
    content_count: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ContentHistoryItem(BaseModel):
    """A single content package in the history list."""
    id: str
    merchant_id: Optional[str] = None
    industry: str
    style: str
    platforms: list[str]
    status: str
    result: Optional[ContentGenerateResult] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
