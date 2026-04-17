import unittest
from pathlib import Path

from pptx_mcp_adapter import (
    DeckEnhancementRequest,
    PowerPointMCPAdapter,
    SlideEnhancement,
    SlideOperation,
)


class AdapterTests(unittest.TestCase):
    def test_from_dict_contract(self):
        payload = {
            "deck_path": "/tmp/deck.pptx",
            "enhancements": {
                "template_name": "DTB_OptionA",
                "apply_layouts": True,
                "add_animations": True,
                "convert_latex": True,
                "speaker_notes": True,
                "run_visual_qa": True,
            },
            "slides": [
                {
                    "slide_number": 1,
                    "operations": [
                        {"type": "notes", "content": "Speaker notes here"},
                        {
                            "type": "animate",
                            "target": "bullet_list_1",
                            "effect": "appear",
                            "by_paragraph": True,
                        },
                    ],
                }
            ],
        }

        request = DeckEnhancementRequest.from_dict(payload)

        self.assertEqual(request.deck_path, Path("/tmp/deck.pptx"))
        self.assertTrue(request.enhancements.apply_layouts)
        self.assertEqual(request.slides[0].slide_number, 1)
        self.assertEqual(request.slides[0].operations[1].target, "bullet_list_1")

    def test_build_tool_plan_maps_to_mcp_tools(self):
        adapter = PowerPointMCPAdapter(
            mcp_probe_cmd=["python", "-c", "print('ok')"],
            mcp_client_bridge_cmd=["python", "-c", "print('ok')"],
            ppt_session_probe_cmd=["python", "-c", "print('ok')"],
        )
        request = DeckEnhancementRequest(
            deck_path=Path("deck.pptx"),
            slides=[
                SlideEnhancement(
                    slide_number=1,
                    operations=[
                        SlideOperation(type="notes", content="hello"),
                        SlideOperation(
                            type="animate",
                            target="bullet_list_1",
                            effect="appear",
                            by_paragraph=True,
                        ),
                    ],
                )
            ],
        )
        request.enhancements.apply_layouts = True
        request.enhancements.template_name = "DTB_OptionA"
        request.enhancements.run_visual_qa = True
        request.enhancements.convert_latex = True

        plan = adapter.build_tool_plan(request)
        tools = [call.tool for call in plan]

        self.assertIn("manage_presentation", tools)
        self.assertIn("list_templates", tools)
        self.assertIn("analyze_template", tools)
        self.assertIn("add_speaker_notes", tools)
        self.assertIn("add_animation", tools)
        self.assertIn("populate_placeholder", tools)
        self.assertIn("slide_snapshot", tools)

    def test_fallback_when_capabilities_missing(self):
        adapter = PowerPointMCPAdapter()
        request = DeckEnhancementRequest(deck_path=Path("deck.pptx"))

        result = adapter.enhance(request)

        self.assertEqual(result.refined_deck_path, Path("deck.pptx"))
        self.assertEqual(result.tool_plan, [])
        self.assertIn("INITIAL_PPTX_BUILT", [stage.value for stage in result.stages])
        self.assertGreaterEqual(len(result.warnings), 1)


if __name__ == "__main__":
    unittest.main()
