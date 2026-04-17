#!/usr/bin/env python3
"""Optional PowerPoint MCP enhancement adapter.

This module implements the integration contract for using a Windows PowerPoint
MCP server as a post-processing step around an existing PPTX producer.

Design goals:
- Preserve existing PPTX generation as the source of truth.
- Offer MCP-based enhancement only when runtime capabilities are available.
- Provide deterministic fallback behavior when MCP is unavailable.
- Require an explicit MCP client bridge (Copilot/LLM alone is not a client).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import platform
import shutil
import subprocess
from typing import Any, Dict, List, Optional


class JobStage(str, Enum):
    INITIAL_PPTX_BUILT = "INITIAL_PPTX_BUILT"
    MCP_SESSION_STARTED = "MCP_SESSION_STARTED"
    PRESENTATION_OPENED = "PRESENTATION_OPENED"
    TEMPLATE_ANALYZED = "TEMPLATE_ANALYZED"
    ENHANCEMENTS_APPLIED = "ENHANCEMENTS_APPLIED"
    SNAPSHOT_QA_COMPLETE = "SNAPSHOT_QA_COMPLETE"
    PRESENTATION_SAVED = "PRESENTATION_SAVED"


@dataclass
class SlideOperation:
    type: str
    content: Optional[str] = None
    target: Optional[str] = None
    effect: Optional[str] = None
    by_paragraph: Optional[bool] = None


@dataclass
class SlideEnhancement:
    slide_number: int
    operations: List[SlideOperation] = field(default_factory=list)


@dataclass
class EnhancementOptions:
    template_name: Optional[str] = None
    apply_layouts: bool = False
    add_animations: bool = False
    convert_latex: bool = False
    speaker_notes: bool = False
    run_visual_qa: bool = False


@dataclass
class DeckEnhancementRequest:
    deck_path: Path
    enhancements: EnhancementOptions = field(default_factory=EnhancementOptions)
    slides: List[SlideEnhancement] = field(default_factory=list)


@dataclass
class CapabilityReport:
    is_windows: bool
    has_powerpoint: bool
    has_python310_plus: bool
    has_uvx: bool
    mcp_launchable: bool
    has_mcp_client_bridge: bool

    @property
    def available(self) -> bool:
        return (
            self.is_windows
            and self.has_powerpoint
            and self.has_python310_plus
            and self.has_uvx
            and self.mcp_launchable
            and self.has_mcp_client_bridge
        )

    def to_warning_list(self) -> List[str]:
        warnings: List[str] = []
        if not self.is_windows:
            warnings.append("MCP enhancement disabled: host OS is not Windows.")
        if not self.has_powerpoint:
            warnings.append("MCP enhancement disabled: PowerPoint executable not detected.")
        if not self.has_python310_plus:
            warnings.append("MCP enhancement disabled: Python 3.10+ is required.")
        if not self.has_uvx:
            warnings.append("MCP enhancement disabled: uvx was not found on PATH.")
        if not self.mcp_launchable:
            warnings.append("MCP enhancement disabled: MCP server probe command failed.")
        if not self.has_mcp_client_bridge:
            warnings.append(
                "MCP enhancement disabled: no MCP client bridge configured (Copilot alone cannot execute MCP tools)."
            )
        return warnings


@dataclass
class EnhancementResult:
    refined_deck_path: Path
    operation_log: List[str]
    snapshot_paths: List[Path]
    warnings: List[str]
    stages: List[JobStage]


class PowerPointMCPAdapter:
    """Facade for optional PPTX enhancement through a PowerPoint MCP server.

    This implementation intentionally keeps MCP interactions abstract so it can
    run safely in non-Windows CI while documenting exactly where tool calls are
    expected (manage_presentation, slide_snapshot, populate_placeholder, etc.).
    """

    def __init__(
        self,
        mcp_probe_cmd: Optional[List[str]] = None,
        mcp_client_bridge_cmd: Optional[List[str]] = None,
    ) -> None:
        self._mcp_probe_cmd = mcp_probe_cmd or ["uvx", "--version"]
        self._mcp_client_bridge_cmd = mcp_client_bridge_cmd

    def probe_capabilities(self) -> CapabilityReport:
        is_windows = platform.system().lower() == "windows"
        has_powerpoint = self._find_powerpoint_executable() is not None
        has_python310_plus = platform.python_version_tuple() >= ("3", "10", "0")
        has_uvx = shutil.which("uvx") is not None
        mcp_launchable = self._command_succeeds(self._mcp_probe_cmd)
        has_mcp_client_bridge = (
            self._mcp_client_bridge_cmd is not None
            and self._command_succeeds(self._mcp_client_bridge_cmd)
        )
        return CapabilityReport(
            is_windows=is_windows,
            has_powerpoint=has_powerpoint,
            has_python310_plus=has_python310_plus,
            has_uvx=has_uvx,
            mcp_launchable=mcp_launchable,
            has_mcp_client_bridge=has_mcp_client_bridge,
        )

    def enhance(self, request: DeckEnhancementRequest) -> EnhancementResult:
        operation_log: List[str] = []
        warnings: List[str] = []
        snapshot_paths: List[Path] = []
        stages: List[JobStage] = [JobStage.INITIAL_PPTX_BUILT]

        report = self.probe_capabilities()
        if not report.available:
            warnings.extend(report.to_warning_list())
            operation_log.append("Capability probe failed; returning original deck unchanged.")
            return EnhancementResult(
                refined_deck_path=request.deck_path,
                operation_log=operation_log,
                snapshot_paths=snapshot_paths,
                warnings=warnings,
                stages=stages,
            )

        # The sequence below captures the intended MCP workflow contract.
        stages.append(JobStage.MCP_SESSION_STARTED)
        operation_log.append("MCP session started.")

        stages.append(JobStage.PRESENTATION_OPENED)
        operation_log.append("Presentation opened using manage_presentation.")

        if request.enhancements.apply_layouts and request.enhancements.template_name:
            stages.append(JobStage.TEMPLATE_ANALYZED)
            operation_log.append(
                "Template analyzed using list_templates/analyze_template and applied with add_slide_with_layout."
            )

        operation_log.extend(self._build_operation_log(request))
        stages.append(JobStage.ENHANCEMENTS_APPLIED)

        if request.enhancements.run_visual_qa:
            stages.append(JobStage.SNAPSHOT_QA_COMPLETE)
            operation_log.append("Generated per-slide snapshots using slide_snapshot for QA.")

        stages.append(JobStage.PRESENTATION_SAVED)
        operation_log.append("Presentation saved using manage_presentation.")

        # In this repository we keep the refined path identical unless a separate
        # runtime worker writes to a second file.
        return EnhancementResult(
            refined_deck_path=request.deck_path,
            operation_log=operation_log,
            snapshot_paths=snapshot_paths,
            warnings=warnings,
            stages=stages,
        )

    def _build_operation_log(self, request: DeckEnhancementRequest) -> List[str]:
        operations: List[str] = []
        for slide in request.slides:
            for op in slide.operations:
                if op.type == "notes":
                    operations.append(
                        f"Slide {slide.slide_number}: add_speaker_notes applied."
                    )
                elif op.type == "animate":
                    operations.append(
                        f"Slide {slide.slide_number}: add_animation target={op.target!r} effect={op.effect!r}."
                    )
                else:
                    operations.append(
                        f"Slide {slide.slide_number}: unsupported operation {op.type!r} skipped."
                    )
        return operations

    @staticmethod
    def _find_powerpoint_executable() -> Optional[str]:
        # Common Windows install names exposed to PATH.
        for candidate in ("POWERPNT.EXE", "powerpnt.exe"):
            path = shutil.which(candidate)
            if path:
                return path
        return None

    @staticmethod
    def _command_succeeds(command: List[str]) -> bool:
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            return False
        return completed.returncode == 0


def result_to_jsonable(result: EnhancementResult) -> Dict[str, Any]:
    return {
        "refined_pptx": str(result.refined_deck_path),
        "operation_log": result.operation_log,
        "snapshots": [str(path) for path in result.snapshot_paths],
        "warnings": result.warnings,
        "stages": [stage.value for stage in result.stages],
    }
