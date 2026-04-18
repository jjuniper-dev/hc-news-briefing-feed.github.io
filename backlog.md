# Backlog

This page is designed to be **searchable** in GitHub (press `t` in repo or use browser find `⌘/Ctrl+F`).
Use IDs, keywords, and tags to quickly locate items.

## Search Index

| ID | Title | Status | Priority | Keywords |
|---|---|---|---|---|
| BL-001 | Agent-Driven PPTX Generation Demo (MCP Pattern) | Planned | High | `pptx`, `mcp`, `workflow`, `python-pptx`, `replit`, `demo`, `deck-generation` |
| BL-002 | Working Prototype of `powerpoint-mcp` | Planned | High | `powerpoint-mcp`, `MacBook`, `compatibility`, `COM`, `prototype`, `tooling` |

---

## BL-001 — Agent-Driven PPTX Generation Demo (MCP Pattern)
**Status:** Planned  
**Priority:** High  
**Type:** Demo / Capability Pattern

### Objective
Demonstrate how AI can generate a structured, governed PPTX artifact from user intent using an MCP-style tool invocation pattern.

### Outcome
A working demo (MacBook-safe) that shows:
- tile or chat-triggered workflow
- visible workflow execution stages
- an “MCP tool call” moment
- preview of slide structure
- simulated or real PPTX generation

### Scope (Included)
- Replit-based UI (Agent Workspace)
- workflow tracker (live task stages)
- agent logic (LLM → structured spec)
- PPTX generator (`python-pptx`)
- preview panel (slide outline or mock thumbnails)
- “rendering to PPTX” step (simulated or real)

### Scope (Excluded for now)
- true MCP protocol implementation
- enterprise deployment
- GC-compliant runtime / ATO
- direct PATH / HAIL integration

### Key Features
1. UX entry via tile such as `Generate ARB Deck` or chat-triggered workflow
2. Workflow tracker stages:
   - Parse request
   - Select template
   - Generate content
   - Format slides
   - Build PPTX
3. MCP pattern simulation with a tool call such as:
   ```json
   {
     "tool": "generate_pptx_deck",
     "params": {
       "template": "EA Option A",
       "slides": 5,
       "topic": "AI Architecture"
     }
   }
   ```
4. Preview panel with slide titles, bullet structure, and optional pseudo-thumbnails
5. Output actions:
   - Download PPTX
   - Regenerate
   - Edit spec

### Tech Stack
- Replit (UI + agent)
- OpenAI / Claude API
- Python backend
- `python-pptx`
- JSON state for workflow tracking

### Success Criteria
- Runs reliably on MacBook
- Workflow visibly progresses
- Clear separation between agent reasoning and tool execution
- Audience understands this as a capability pattern, not a toy

### Strategic Value
Demonstrates the shift from manual artifact creation to reusable AI capability, supporting faster architecture delivery, standardized outputs, and platform-based thinking.

### Tags
`#pptx` `#mcp-pattern` `#agent-workflow` `#replit` `#python-pptx` `#artifact-generation`

---

## BL-002 — Working Prototype of `powerpoint-mcp`
**Status:** Planned  
**Priority:** High  
**Type:** Prototype / Evaluation

### Objective
Create a working prototype based on Ayush Maniar’s `powerpoint-mcp` project:
https://github.com/Ayushmaniar/powerpoint-mcp

### Outcome
A local demo-ready implementation that proves the MCP-to-PowerPoint pattern and can be shown on MacBook as part of the broader artifact-generation concept.

### Focus
- understand the repo architecture and tool model
- determine MacBook-compatible demo path
- identify what must be simulated versus what can work natively
- produce a working or near-working prototype suitable for demonstration

### Potential Approaches
- direct evaluation of repo components and dependencies
- adapt pattern to a Mac-safe mock/prototype
- replace Windows COM-dependent pieces with a portable generation layer
- preserve the MCP-shaped interaction even if the backend is partially simulated

### Success Criteria
- prototype can be demonstrated live
- shows the concept clearly
- supports the narrative of AI invoking artifact-generation tools
- helps inform a longer-term governed PPTX generation capability

### Tags
`#powerpoint-mcp` `#macbook-demo` `#prototype` `#compatibility` `#tool-invocation`

---

## Suggested Next Actions
- [ ] Define acceptance test script for BL-001 demo flow.
- [ ] Spike Mac-safe rendering path (`python-pptx`-first fallback).
- [ ] Add lightweight UI mock for workflow tracker + tool-call event.
- [ ] Record known constraints (COM-only components, simulation boundaries).
