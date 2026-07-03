"""LangChain multi-stage content generation service."""
from __future__ import annotations

import json
import logging
import re
import os
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import settings
from app.models.pydantic_models import (
    AnglesOutput,
    ContentGenerateResult,
    PlatformPost,
    PostsOutput,
    PostsOutput,
    ViralAngle,
)

logger = logging.getLogger(__name__)

# Module-level LLM instance
_llm = ChatOpenAI(
    response_format={"type": "json_object"},
    model=settings.openai_model_name or os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini"),
    temperature=settings.openai_temperature,
    api_key=settings.openai_api_key or os.environ.get("OPENAI_API_KEY", ""),
    base_url=settings.openai_api_base or os.environ.get("OPENAI_API_BASE", ""),
)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

ANGLES_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是一个严格的JSON生成器。你必须且只能返回一个包含angles数组的JSON对象，每个对象必须包含title、hook、angle_description三个字符串键。绝不能包含任何Markdown标记或```符号。你是一位顶级中文爆款内容策划大师。"),
    ("human", "行业：{industry}\n风格：{style}\n请生成3个爆款内容切入点（角度），以JSON格式返回。"),
])

SCRIPT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是一个严格的JSON生成器。你必须且只能返回一个包含posts数组的JSON对象，每个对象必须包含platform、title、body、tags(数组)、visual_suggestion五个键。绝不能包含任何Markdown标记。你是一位专业的中文社交媒体文案写手。"),
    ("human", "行业：{industry}\n风格：{style}\n目标平台：{platforms}\n以下是要用的爆款角度：\n{angles}\n请生成各平台内容，以JSON格式返回。"),
])

# ---------------------------------------------------------------------------
# Fallback parser
# ---------------------------------------------------------------------------

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?```", re.DOTALL)


def _strip_markdown_fence(raw: str) -> str:
    content = raw.strip()
    # Try ```json ... ``` first
    match = _JSON_BLOCK_RE.search(content)
    if match:
        return match.group(1).strip()
    # No code fence: find first { and last }
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        return content[start:end+1]
    return content


# ---------------------------------------------------------------------------
# Public generation function
# ---------------------------------------------------------------------------


async def generate_content(
    industry: str,
    style: str,
    platforms: list[str],
) -> ContentGenerateResult:
    logger.info("Stage 1: Generating angles for industry=%s style=%s", industry, style)

    angle_chain = ANGLES_PROMPT | _llm.with_structured_output(
        schema=AnglesOutput, method="json_mode"
    )

    angles: list[ViralAngle] = []
    try:
        angles_output: AnglesOutput = await angle_chain.ainvoke(
            {"industry": industry, "style": style}
        )
        angles = angles_output.angles
    except Exception as exc:
        logger.warning("Stage 1 failed (%s); falling back.", exc)
        angles = await _fallback_angles(industry, style)

    if not angles:
        raise ValueError("Stage 1 produced zero angles.")

    angles_text = "\n".join(
        f"[{i+1}] {a.title}: {a.hook} ({a.angle_description})"
        for i, a in enumerate(angles)
    )

    logger.info("Stage 2: Generating posts for %d angles", len(angles))

    script_chain = SCRIPT_PROMPT | _llm.with_structured_output(
        schema=PostsOutput, method="json_mode"
    )

    all_posts: list[PlatformPost] = []
    try:
        posts_output: PostsOutput = await script_chain.ainvoke({
            "industry": industry,
            "style": style,
            "platforms": ", ".join(platforms),
            "angles": angles_text,
        })
        all_posts = posts_output.posts
    except Exception as exc:
        logger.warning("Stage 2 failed (%s); falling back.", exc)
        all_posts = await _fallback_posts(industry, style, platforms, angles_text)

    return ContentGenerateResult(
        industry=industry,
        style=style,
        platforms=platforms,
        angles=angles,
        posts=all_posts,
    )


async def _fallback_angles(industry: str, style: str) -> list[ViralAngle]:
    chain = ANGLES_PROMPT | _llm
    raw = await chain.ainvoke({"industry": industry, "style": style})
    content = _strip_markdown_fence(raw.content if hasattr(raw, "content") else str(raw))
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            raw_list = parsed.get("angles", [parsed])
        else:
            raw_list = parsed if isinstance(parsed, list) else [parsed]
        return [ViralAngle(**item) for item in raw_list]
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"Failed to parse angles. Content:\n{content[:500]}") from exc


async def _fallback_posts(
    industry: str, style: str, platforms: list[str], angles_text: str,
) -> list[PlatformPost]:
    chain = SCRIPT_PROMPT | _llm
    raw = await chain.ainvoke({
        "industry": industry,
        "style": style,
        "platforms": ", ".join(platforms),
        "angles": angles_text,
    })
    content = _strip_markdown_fence(raw.content if hasattr(raw, "content") else str(raw))
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            raw_list = parsed.get("posts", [parsed])
        else:
            raw_list = parsed if isinstance(parsed, list) else [parsed]
        return [PlatformPost(**item) for item in raw_list]
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"Failed to parse posts. Content:\n{content[:500]}") from exc
