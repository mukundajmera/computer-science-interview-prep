# GenAI-Era Case Study Research Plan

This plan keeps GenAI-era company case studies source-backed before they become portal-discovered learner content. Do not create additional target case-study folders until the current facts below have been verified from public primary sources during the implementation turn.

## Target Case Studies

| Target | Future path | Primary learning question | Status |
|---|---|---|---|
| ChatGPT Inference | `case-studies/chatgpt-inference/README.md` | How do large-scale assistant products balance routing, latency, cost, memory, tools, multimodality, and safety controls? | Implemented with public primary-source caveats on 2026-06-14 |
| GitHub Copilot | `case-studies/github-copilot/README.md` | How do coding assistants collect context, retrieve project signals, route models, preserve latency, and enforce enterprise controls? | Implemented with public primary-source caveats on 2026-06-14 |

## Required Source Standard

Use public primary sources first:

- Official product docs.
- Official engineering blogs.
- Official system cards, safety reports, model cards, or evaluation disclosures.
- Official pricing pages when discussing inference economics.
- SEC filings, investor materials, or official earnings materials when citing adoption or scale.

Use reputable secondary sources only when the case study explicitly labels them as secondary and primary sources are unavailable for that claim.

## Metric Table Contract

Every concrete scale or adoption claim must use this table shape:

| Metric | Value | As of | Source | Notes |
|---|---|---|---|---|
| Example metric | Do not fill until verified | YYYY-MM-DD | Primary source link | Include caveat, scope, or definition |

Do not convert historical, approximate, or secondary figures into current facts. If a metric cannot be verified, omit it or label it as unknown.

## ChatGPT Inference Research Checklist

Verified for the 2026-06-14 implementation:

- Current enterprise product surface, including agents, connectors, security posture, and adoption claim, from OpenAI's ChatGPT Enterprise page.
- Enterprise launch controls and historical Fortune 500 registered-account signal from OpenAI's launch article.
- Agent-platform tool capabilities from OpenAI's Responses API and Agents SDK announcement.
- Data-use default for business products from OpenAI's help-center data-use article.

Verify again before materially changing:

- Current product surfaces: chat, tools, search/browsing, voice/realtime, memory, enterprise controls, and multimodal behavior.
- Current model-family and routing claims; avoid guessing exact production routing.
- Current scale or adoption claims if used.
- Context-window, latency, and pricing inputs if used in cost analysis.
- Safety and evaluation practices from official system cards, prepared-framework documents, or product docs.
- Data-control claims for enterprise or team usage.

Repository cross-links to use after verification:

- [Model Routing and Orchestration](../06-genai-systems/00-concepts/model-routing-orchestration/)
- [Streaming and KV Cache](../06-genai-systems/00-concepts/streaming-kv-cache/)
- [Token Cost and Latency](../06-genai-systems/00-concepts/token-cost-latency/)
- [Safety Governance](../06-genai-systems/00-concepts/safety-governance/)
- [LLM Evaluation](../06-genai-systems/00-concepts/llm-evaluation/)
- [Multi-Tenant Chat Assistant HLD](../06-genai-systems/02-llm-hld-projects/multi-tenant-chat-assistant/)
- [LLM Evaluation and Safety Platform](../06-genai-systems/02-llm-hld-projects/llm-evaluation-safety-platform/)

## GitHub Copilot Research Checklist

Verified for the 2026-06-14 implementation:

- Cloud-agent workflow, repository scope, ephemeral GitHub Actions environment, and session timeout from GitHub Docs.
- Security validation mitigations from GitHub Docs.
- Content exclusion and MCP extension points from GitHub Docs.
- Model/billing and utility-model control-plane facts from GitHub Docs.
- Agent-mode product evolution from GitHub Blog.

Verify again before materially changing:

- Current product surfaces: IDE completions, chat, agent mode, code review, CLI, workspaces, and enterprise administration.
- Current model/provider options and any routing claims.
- Current adoption, organization, or productivity metrics if used.
- Context collection, repository indexing, retrieval, prompt assembly, and latency claims.
- Privacy, data retention, enterprise policy, and public-code filtering claims.
- Security and vulnerability-filtering claims.
- Current pricing or plan limits if used.

Repository cross-links to use after verification:

- [AI Coding Copilot HLD](../06-genai-systems/02-llm-hld-projects/ai-coding-copilot/)
- [Semantic Retrieval Platform](../06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/)
- [Conversation Memory Store](../06-genai-systems/01-llm-lld-projects/conversation-memory-store/)
- [Tool Router](../06-genai-systems/01-llm-lld-projects/tool-router/)
- [Safety Governance](../06-genai-systems/00-concepts/safety-governance/)

## Drafting Rules

1. Start each case study with the existing case-study structure: problem statement, architecture evolution, key decisions, technologies, trade-offs, lessons, and interview relevance.
2. Separate observed public facts from interview-oriented inference.
3. Use diagrams from repository concepts where possible; add Mermaid `.mmd` sources for new architecture diagrams.
4. Link lessons back to GenAI concepts and HLD projects rather than duplicating full explanations.
5. Run markdown links, case-study inventory, and portal build before publishing a case-study folder.

## Validation Plan

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py case-studies/GENAI-ERA-RESEARCH-PLAN.md
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py --sections case-studies
npm --prefix apps/portal run build
git diff --check
```
