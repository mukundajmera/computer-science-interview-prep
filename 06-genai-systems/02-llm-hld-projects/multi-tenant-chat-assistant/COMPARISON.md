# Multi-Tenant Chat Assistant Platform — Comparison

## System Comparison

| System | Similarity | Key difference |
|---|---|---|
| Single-Tenant Chat App | Core chat and LLM interaction | Strict isolation and configurable policies per tenant |
| API Gateway | Routing, auth, rate limiting | Deep inspection of GenAI payload, prompt assembly, output filtering |
| Multi-tenant SaaS (e.g. CRM) | Data isolation, tiered billing | Real-time streaming nature, heavy reliance on third-party LLMs |
| Workflow Orchestration | Executing ordered steps | Dynamic natural language flow vs rigid state machine |

## Migration and reuse
- **Identity and Access Management:** Reuse existing OAuth/SAML integrations for tenant login.
- **Data Isolation:** PostgreSQL Row Level Security (RLS) patterns can be reused from traditional multi-tenant SaaS.
- **Analytics Pipeline:** The ClickHouse/Redis combo for tracking billing can be reused across other API consumption models.
- **Model Gateway:** A well-abstracted Model Router can be spun out as an internal LLM Gateway for other GenAI projects within the company.