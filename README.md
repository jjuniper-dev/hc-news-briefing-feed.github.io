# hc-news-briefing-feed.github.io

This repository hosts a lightweight news dashboard that publishes a daily briefing and monitors the health of several RSS feeds. The site is deployed via GitHub Pages and the data is refreshed automatically using GitHub Actions.

See [ARCHITECTURE.md](ARCHITECTURE.md) for an overview of how the pieces fit together.

## Optional PowerPoint refinement adapter

If you generate PPTX briefings externally, this repo includes `pptx_mcp_adapter.py` as an **optional** post-processor integration point for a Windows-hosted PowerPoint MCP runtime.

The intended operating model is:

- baseline PPTX generation remains the source of truth
- MCP enhancement is a best-effort refinement pass
- fallback is always the original generated deck when capabilities are missing
- a separate MCP client bridge is required for execution (Copilot can assist development/orchestration but is not an MCP runtime client by itself)

The adapter includes:

- `DeckEnhancementRequest.from_dict(...)` for a neutral JSON contract
- `build_tool_plan(...)` for deterministic translation into MCP tool calls
- staged job output and graceful fallback when required runtime capabilities are missing
