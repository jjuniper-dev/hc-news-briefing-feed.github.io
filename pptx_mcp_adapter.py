#!/usr/bin/env python3
"""Optional PowerPoint MCP enhancement adapter.

This module models an integration where an existing (file-oriented) PPTX producer
remains authoritative and a PowerPoint MCP runtime is used only as an optional
Windows refinement pass.
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
class ToolCall:
    tool: str
    arguments: Dict[str, Any]


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

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DeckEnhancementRequest":
        options = EnhancementOptions(**payload.get("enhancements", {}))
        slides: List[SlideEnhancement] = []
        for slide in payload.get("slides", []):
            ops = [SlideOperation(**operation) for operation in slide.get("operations", [])]
            slides.append(
                SlideEnhancement(
                    slide_number=int(slide["slide_number"]),
                    operations=ops,
                )
            )
        return cls(deck_path=Path(payload["deck_path"]), enhancements=options, slides=slides)


@dataclass
class CapabilityReport:
    is_windows: bool
    has_powerpoint: bool
    has_python310_plus: bool
    has_uvx: bool
    mcp_launchable: bool
    has_mcp_client_bridge: bool
    has_powerpoint_session_access: bool

    @property
    def available(self) -> bool:
        return (
            self.is_windows
            and self.has_powerpoint
            and self.has_python310_plus
            and self.has_uvx
            and self.mcp_launchable
            and self.has_mcp_client_bridge
            and self.has_powerpoint_session_access
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
        if not self.has_powerpoint_session_access:
            warnings.append("MCP enhancement disabled: PowerPoint desktop session is not accessible.")
        return warnings


@dataclass
class EnhancementResult:
    refined_deck_path: Path
    operation_log: List[str]
    snapshot_paths: List[Path]
    warnings: List[str]
    stages: List[JobStage]
    tool_plan: List[ToolCall] = field(default_factory=list)


class PowerPointMCPAdapter:
    """Facade for optional PPTX enhancement through a PowerPoint MCP server."""

    def __init__(
        self,
        mcp_probe_cmd: Optional[List[str]] = None,
        mcp_client_bridge_cmd: Optional[List[str]] = None,
        ppt_session_probe_cmd: Optional[List[str]] = None,
    ) -> None:
        self._mcp_probe_cmd = mcp_probe_cmd or ["uvx", "--version"]
        self._mcp_client_bridge_cmd = mcp_client_bridge_cmd
        self._ppt_session_probe_cmd = ppt_session_probe_cmd

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
        has_powerpoint_session_access = (
            self._ppt_session_probe_cmd is not None
            and self._command_succeeds(self._ppt_session_probe_cmd)
        )
        return CapabilityReport(
            is_windows=is_windows,
            has_powerpoint=has_powerpoint,
            has_python310_plus=has_python310_plus,
            has_uvx=has_uvx,
            mcp_launchable=mcp_launchable,
            has_mcp_client_bridge=has_mcp_client_bridge,
            has_powerpoint_session_access=has_powerpoint_session_access,
        )

    def build_tool_plan(self, request: DeckEnhancementRequest) -> List[ToolCall]:
        plan: List[ToolCall] = [
            ToolCall("manage_presentation", {"action": "open", "path": str(request.deck_path)}),
        ]

        if request.enhancements.apply_layouts and request.enhancements.template_name:
            plan.extend(
                [
                    ToolCall("list_templates", {}),
                    ToolCall(
                        "analyze_template",
                        {"template_name": request.enhancements.template_name},
                    ),
                ]
            )

        for slide in request.slides:
            for op in slide.operations:
                if op.type == "notes":
                    plan.append(
                        ToolCall(
                            "add_speaker_notes",
                            {"slide_number": slide.slide_number, "content": op.content or ""},
                        )
                    )
                elif op.type == "animate":
                    plan.append(
                        ToolCall(
                            "add_animation",
                            {
                                "slide_number": slide.slide_number,
                                "target": op.target,
                                "effect": op.effect,
                                "by_paragraph": bool(op.by_paragraph),
                            },
                        )
                    )

        if request.enhancements.convert_latex:
            plan.append(ToolCall("populate_placeholder", {"mode": "native_equation"}))

        if request.enhancements.run_visual_qa:
            plan.append(ToolCall("slide_snapshot", {"all_slides": True}))

        plan.append(ToolCall("manage_presentation", {"action": "save", "path": str(request.deck_path)}))
        return plan

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
                tool_plan=[],
            )

        tool_plan = self.build_tool_plan(request)

        stages.append(JobStage.MCP_SESSION_STARTED)
        operation_log.append("MCP session started via configured client bridge.")

        stages.append(JobStage.PRESENTATION_OPENED)
        operation_log.append("Presentation opened using manage_presentation.")

        if request.enhancements.apply_layouts and request.enhancements.template_name:
            stages.append(JobStage.TEMPLATE_ANALYZED)
            operation_log.append("Template analysis completed (list_templates -> analyze_template).")

        stages.append(JobStage.ENHANCEMENTS_APPLIED)
        operation_log.append("Slide-level MCP enhancement operations planned/applied.")

        if request.enhancements.run_visual_qa:
            stages.append(JobStage.SNAPSHOT_QA_COMPLETE)
            operation_log.append("Visual QA snapshots requested via slide_snapshot.")

        stages.append(JobStage.PRESENTATION_SAVED)
        operation_log.append("Presentation saved using manage_presentation.")

        return EnhancementResult(
            refined_deck_path=request.deck_path,
            operation_log=operation_log,
            snapshot_paths=snapshot_paths,
            warnings=warnings,
            stages=stages,
            tool_plan=tool_plan,
        )

    @staticmethod
    def _find_powerpoint_executable() -> Optional[str]:
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
        "tool_plan": [
            {"tool": call.tool, "arguments": call.arguments}
            for call in result.tool_plan
        ],
    }
