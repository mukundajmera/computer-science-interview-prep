import os
import sys
from pathlib import Path
import importlib.util
import pytest

PATTERN_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, PATTERN_DIR / rel_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


chain_v1 = load_module("chain_v1", "python/v1-basic/chain_demo.py")
middleware = load_module("middleware", "python/v2-variant/middleware_pipeline.py")
security = load_module("security", "python/v3-advanced/security_filter_chain.py")


def test_handler_processes_request():
    faq = chain_v1.FAQHandler()
    t1 = chain_v1.SupportTicket("Forgot password", 1)
    t2 = chain_v1.SupportTicket("Server crash", 2)
    assert faq.can_handle(t1) is True
    assert faq.can_handle(t2) is False
    faq.handle(t1)


def test_chain_passes_to_next():
    faq = chain_v1.FAQHandler()
    l1 = chain_v1.Level1Support()
    l2 = chain_v1.Level2Support()
    mgr = chain_v1.ManagerSupport()
    faq.set_next(l1).set_next(l2).set_next(mgr)

    faq.handle(chain_v1.SupportTicket("Login issue", 2))
    faq.handle(chain_v1.SupportTicket("Performance drop", 3))
    faq.handle(chain_v1.SupportTicket("Outage incident", 5))


def test_no_handler_does_not_throw():
    faq = chain_v1.FAQHandler()
    unhandled = chain_v1.SupportTicket("Critical breach", 99)
    faq.handle(unhandled)


# --- v2-variant Tests ---

def test_middleware_pipeline_success_and_short_circuits():
    pipeline = middleware.AuthMiddleware()
    pipeline.link_with(middleware.RateLimitMiddleware(max_per_minute=2)).link_with(middleware.SanitizationMiddleware())

    # Valid request
    req1 = middleware.HttpRequest("/api/users", "Bearer valid_key", "valid payload", "192.168.1.1")
    res1 = pipeline.handle(req1)
    assert res1.status_code == 200
    assert res1.is_success is True

    # Missing token -> 401
    req2 = middleware.HttpRequest("/api/users", None, "valid", "192.168.1.1")
    res2 = pipeline.handle(req2)
    assert res2.status_code == 401
    assert res2.is_success is False

    # Malicious script tag -> 400
    req3 = middleware.HttpRequest("/api/users", "Bearer valid_key", "<script>bad</script>", "192.168.1.2")
    res3 = pipeline.handle(req3)
    assert res3.status_code == 400

    # Rate limiting on third request from same IP
    req_rl = middleware.HttpRequest("/api/users", "Bearer valid_key", "payload", "192.168.1.1")
    pipeline.handle(req_rl)
    res_exceeded = pipeline.handle(req_rl)
    assert res_exceeded.status_code == 429


# --- v3-advanced Tests ---

def test_security_filter_chain_ordering_and_auditing():
    chain = security.SecurityFilterChain()
    # Add in reverse order; chain should re-sort by priority
    chain.add_filter(security.RoleValidationFilter("ADMIN"))
    chain.add_filter(security.BlacklistFilter())

    ctx_valid = security.SecurityContext("alice", ["ADMIN", "DEV"])
    assert chain.execute(ctx_valid) is True
    assert any("PASSED" in a for a in ctx_valid.audit_trail)

    ctx_banned = security.SecurityContext("banned_user_1", ["ADMIN"])
    assert chain.execute(ctx_banned) is False
    assert any("BLOCKED: User is blacklisted" in a for a in ctx_banned.audit_trail)

    ctx_norole = security.SecurityContext("bob", ["GUEST"])
    assert chain.execute(ctx_norole) is False
    assert any("Missing required role" in a for a in ctx_norole.audit_trail)
