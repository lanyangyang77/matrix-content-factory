"""SQLAlchemy ORM models for the Matrix Biz Automation System."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Helper: auto-generated UUID primary key
# ---------------------------------------------------------------------------

def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.utcnow()


class TimestampMixin:
    """Adds `created_at` and `updated_at` timestamp columns."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=_utcnow, onupdate=_utcnow, nullable=False
    )


# ---------------------------------------------------------------------------
# 1. tenants
# ---------------------------------------------------------------------------

class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tier: Mapped[str] = mapped_column(
        String(50), nullable=False, default="free"
    )  # free | pro | enterprise
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # relationships
    users: Mapped[list["User"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    matrix_accounts: Mapped[list["MatrixAccount"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    content_packages: Mapped[list["ContentPackage"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    crm_leads: Mapped[list["CRMLead"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    merchant_profiles: Mapped[list["MerchantProfile"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 2. users
# ---------------------------------------------------------------------------

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")  # owner | admin | member
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="users")


# ---------------------------------------------------------------------------
# 3. matrix_accounts
# ---------------------------------------------------------------------------

class MatrixAccount(Base, TimestampMixin):
    """A social / content-platform account managed by a tenant."""
    __tablename__ = "matrix_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False
    )
    platform_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # Douyin | Xiaohongshu | WeChat | Kuaishou | Bilibili | etc.
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )  # active | suspended | expired
    credentials: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # encrypted token / cookie payload
    metadata_: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata", JSON, nullable=True
    )  # followers, platform-specific stats

    # relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="matrix_accounts")


# ---------------------------------------------------------------------------
# 4. content_packages
# ---------------------------------------------------------------------------

class ContentPackage(Base, TimestampMixin):
    """A batch of generated content items for a single brief."""
    __tablename__ = "content_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False
    )
    merchant_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("merchant_profiles.id"), nullable=True, index=True
    )
    task_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )  # Celery task ID for async generation
    industry: Mapped[str] = mapped_column(String(255), nullable=False)
    style: Mapped[str] = mapped_column(String(255), nullable=False)
    platforms: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)  # list of platform names
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending | processing | completed | failed
    brief: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # human-readable brief
    generated_angles: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # Step-1 output (list of angle strings)
    result: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # Step-2 final JSON array (title, body, tags, image_prompt)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # relationships
    merchant: Mapped[Optional["MerchantProfile"]] = relationship(back_populates="content_packages")
    tenant: Mapped["Tenant"] = relationship(back_populates="content_packages")


# ---------------------------------------------------------------------------
# 5. crm_leads
# ---------------------------------------------------------------------------

class CRMLead(Base, TimestampMixin):
    """A prospective customer lead tracked by the tenant."""
    __tablename__ = "crm_leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_info: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # phone, email, WeChat ID, etc.
    source_channel: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # douyin_ad | xiaohongshu_organic | referral | cold_call | etc.
    ai_tags: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # {"intent": "high", "budget": "50k+", "industry": "ecommerce"}
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="new"
    )  # new | contacted | qualified | proposal | negotiation | won | lost
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # AI-predicted lead score
    interaction_history: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # array of interaction events
    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="crm_leads")
    assignee: Mapped[Optional["User"]] = relationship()


# ---------------------------------------------------------------------------
# 6. merchant_profiles
# ---------------------------------------------------------------------------

class MerchantProfile(Base, TimestampMixin):
    """A merchant/business client whose content we manage."""
    __tablename__ = "merchant_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False
    )
    merchant_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(255), nullable=False)
    target_audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="merchant_profiles")
    content_packages: Mapped[list["ContentPackage"]] = relationship(
        back_populates="merchant", cascade="all, delete-orphan"
    )
