"""Pydantic models for layout sections (incremental migration).

This module will gradually host strongly-typed models that mirror the JSON
shapes emitted by the builder. We introduce them model-by-model to keep
changes reviewable and tests green between commits.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Macro(BaseModel):
    """Macro section entry.

    Matches the structure produced by MacroSpec.to_dict() today.
    Unknown keys are forbidden; field aliases match the JSON casing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    description: Optional[str] = None
    bindings: List[Dict]
    params: List[str] = Field(default_factory=list)
    waitMs: Optional[int] = None
    tapMs: Optional[int] = None


class HoldTap(BaseModel):
    """Hold-tap behavior entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    description: Optional[str] = None
    bindings: List[str]
    tappingTermMs: Optional[int] = None
    flavor: Optional[str] = None
    quickTapMs: Optional[int] = None
    requirePriorIdleMs: Optional[int] = None
    holdTriggerOnRelease: Optional[bool] = None
    holdTriggerKeyPositions: Optional[List[int]] = None


__all__ = ["Macro", "HoldTap"]
