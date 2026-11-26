import pytest
import time
import sys
import threading
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import importlib.util
import types

def load_gateway_module(ver: str, folder: str):
    path = os.path.join(os.path.dirname(__file__), '..', folder, 'api_gateway.py')
    spec = importlib.util.spec_from_file_location(f"{ver}.api_gateway", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pkg = types.ModuleType(ver)
    pkg.api_gateway = mod
    sys.modules[ver] = pkg
    sys.modules[f"{ver}.api_gateway"] = mod
    return mod

for _ver, _f in [('v1_basic', 'v1-basic'), ('v2_extended', 'v2-extended'), ('v3_optimized', 'v3-optimized')]:
    load_gateway_module(_ver, _f)

def clear_modules():
    for _ver, _f in [('v1_basic', 'v1-basic'), ('v2_extended', 'v2-extended'), ('v3_optimized', 'v3-optimized')]:
        load_gateway_module(_ver, _f)

# ---- v1 tests ----
def test_v1_basic_routing():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    gw.register_backend("users", lambda req: Response(200, {}, "Users Data"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    res = gw.handle(req)
    assert res.status_code == 200
    assert res.body == "Users Data"

def test_v1_not_found():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    req = Request("/api/unknown", "GET", {})
    res = gw.handle(req)
    assert res.status_code == 404

def test_v1_auth_filter_unauthorized():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response, AuthFilter
    gw = ApiGateway()
    gw.add_pre_filter(AuthFilter())
    gw.register_backend("users", lambda req: Response(200, {}, "Users Data"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    res = gw.handle(req)
    assert res.status_code == 401

def test_v1_auth_filter_authorized():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response, AuthFilter
    gw = ApiGateway()
    gw.add_pre_filter(AuthFilter())
    gw.register_backend("users", lambda req: Response(200, {}, "Users Data"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {"Authorization": "Bearer token"})
    res = gw.handle(req)
    assert res.status_code == 200
    
def test_v1_backend_error():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    
    def failing_backend(req):
        raise Exception("DB Error")
        
    gw.register_backend("users", failing_backend)
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "POST", {})
    res = gw.handle(req)
    assert res.status_code == 500

def test_v1_bounded_request_body():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    gw.register_backend("users", lambda req: Response(200, {}, "OK"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "POST", {}, "a" * (1024 * 1024 + 1))
    res = gw.handle(req)
    assert res.status_code == 413
    
def test_v1_downstream_cancellation():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    gw.register_backend("users", lambda req: Response(200, {}, "OK"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    req.is_cancelled = True
    res = gw.handle(req)
    assert res.status_code == 499

def test_v1_deadline_propagation():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response
    import time
    gw = ApiGateway()
    gw.register_backend("users", lambda req: Response(200, {}, "OK"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    req.deadline_ms = int(time.time() * 1000) - 1000
    res = gw.handle(req)
    assert res.status_code == 504

def test_v1_duplicate_retry_eligibility():
    clear_modules()
    from v1_basic.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    
    calls = [0]
    def flaky_backend(req):
        calls[0] += 1
        if calls[0] == 1:
            raise Exception("DB Error")
        return Response(200, {}, "OK")
        
    gw.register_backend("users", flaky_backend)
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    res = gw.handle(req)
    assert res.status_code == 200
    assert calls[0] == 2

# ---- v2 tests ----
def test_v2_rate_limiting():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response, RateLimitFilter
    gw = ApiGateway()
    
    gw.add_filter(RateLimitFilter(max_requests=2, window_sec=1))
    gw.register_backend("users", lambda req: Response(200, {}, "Users Data"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {"Client-ID": "test_client"})
    assert gw.handle(req).status_code == 200
    assert gw.handle(req).status_code == 200
    assert gw.handle(req).status_code == 429
    
def test_v2_logging_filter():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response, LoggingFilter
    gw = ApiGateway()
    
    logger = LoggingFilter()
    gw.add_filter(logger)
    gw.register_backend("users", lambda req: Response(200, {}, "Users Data"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    gw.handle(req)
    assert len(logger.logs) == 1
    assert "Response code: 200" in logger.logs[0]

def test_v2_multiple_filters():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response, AuthFilter, RateLimitFilter
    gw = ApiGateway()
    
    gw.add_filter(AuthFilter())
    gw.add_filter(RateLimitFilter(max_requests=2, window_sec=1))
    gw.register_backend("users", lambda req: Response(200, {}, "Users Data"))
    gw.add_route("/api/users", "users")
    
    req1 = Request("/api/users/1", "GET", {"Client-ID": "test"})
    assert gw.handle(req1).status_code == 401
    
    req2 = Request("/api/users/1", "GET", {"Authorization": "token", "Client-ID": "test"})
    assert gw.handle(req2).status_code == 200

def test_v2_route_not_found():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    
    req = Request("/unknown", "GET", {})
    assert gw.handle(req).status_code == 404

def test_v2_backend_unavailable():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    gw.add_route("/api", "unknown_backend")
    
    req = Request("/api/test", "GET", {})
    assert gw.handle(req).status_code == 503

def test_v2_bounded_request_body():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    gw.register_backend("users", lambda req: Response(200, {}, "OK"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "POST", {}, "a" * (1024 * 1024 + 1))
    res = gw.handle(req)
    assert res.status_code == 413
    
def test_v2_downstream_cancellation():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    gw.register_backend("users", lambda req: Response(200, {}, "OK"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    req.is_cancelled = True
    res = gw.handle(req)
    assert res.status_code == 499

def test_v2_deadline_propagation():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response
    import time
    gw = ApiGateway()
    gw.register_backend("users", lambda req: Response(200, {}, "OK"))
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    req.deadline_ms = int(time.time() * 1000) - 1000
    res = gw.handle(req)
    assert res.status_code == 504

def test_v2_duplicate_retry_eligibility():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    
    calls = [0]
    def flaky_backend(req):
        calls[0] += 1
        if calls[0] == 1:
            raise Exception("DB Error")
        return Response(200, {}, "OK")
        
    gw.register_backend("users", flaky_backend)
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    res = gw.handle(req)
    assert res.status_code == 200
    assert calls[0] == 2

def test_v2_filter_short_circuit_and_order():
    clear_modules()
    from v2_extended.api_gateway import ApiGateway, Request, Response, Filter
    gw = ApiGateway()
    order = []
    
    class Filter1(Filter):
        def pre_filter(self, req):
            order.append("pre1")
            return None
        def post_filter(self, res):
            order.append("post1")
            return res
            
    class Filter2(Filter):
        def pre_filter(self, req):
            order.append("pre2-short-circuit")
            return Response(401, {}, "Stop")
        def post_filter(self, res):
            order.append("post2")
            return res
            
    class Filter3(Filter):
        def pre_filter(self, req):
            order.append("pre3")
            return None
        def post_filter(self, res):
            order.append("post3")
            return res

    gw.add_filter(Filter1())
    gw.add_filter(Filter2())
    gw.add_filter(Filter3())
    
    def backend(req):
        order.append("backend")
        return Response(200, {}, "OK")
        
    gw.register_backend("users", backend)
    gw.add_route("/api/users", "users")
    
    req = Request("/api/users/1", "GET", {})
    res = gw.handle(req)
    
    assert res.status_code == 401
    assert len(order) == 3
    assert order[0] == "pre1"
    assert order[1] == "pre2-short-circuit"
    assert order[2] == "post1" # post2 should NOT be called because pre2 returned response

# ---- v3 tests ----
def test_v3_circuit_breaker():
    clear_modules()
    from v3_optimized.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    
    def failing_backend(req):
        return Response(500, {}, "Error")
        
    gw.register_backend("flaky", failing_backend)
    gw.add_route("/api", "flaky")
    
    req = Request("/api/test", "GET", {})
    
    # 3 failures to trigger circuit breaker (default threshold)
    assert gw.handle(req).status_code == 500
    assert gw.handle(req).status_code == 500
    assert gw.handle(req).status_code == 500
    
    # 4th request should fail fast with 503
    res = gw.handle(req)
    assert res.status_code == 503
    assert "Circuit Open" in res.body

def test_v3_circuit_breaker_recovery():
    clear_modules()
    from v3_optimized.api_gateway import ApiGateway, Request, Response
    gw = ApiGateway()
    
    backend_status = 500
    def dynamic_backend(req):
        return Response(backend_status, {}, "Dynamic")
        
    gw.register_backend("dynamic", dynamic_backend)
    gw.add_route("/api", "dynamic")
    gw.circuit_breakers["dynamic"].reset_timeout = 1  # 1 second timeout
    
    req = Request("/api/test", "GET", {})
    
    # Trip breaker
    gw.handle(req)
    gw.handle(req)
    gw.handle(req)
    assert gw.handle(req).status_code == 503
    
    # Wait for timeout
    time.sleep(1.1)
    
    # Half-open success
    backend_status = 200
    assert gw.handle(req).status_code == 200
    
    # Fully closed now
    assert gw.circuit_breakers["dynamic"].state == "CLOSED"

def test_v3_concurrent_rate_limiting():
    clear_modules()
    from v3_optimized.api_gateway import ApiGateway, Request, Response, RateLimitFilter
    gw = ApiGateway()
    gw.add_filter(RateLimitFilter(max_requests=5, window_sec=1))
    gw.register_backend("users", lambda req: Response(200, {}, "Users Data"))
    gw.add_route("/api/users", "users")
    
    results = []
    
    def worker():
        req = Request("/api/users/1", "GET", {"Client-ID": "concurrent_test"})
        results.append(gw.handle(req).status_code)
        
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    successes = len([r for r in results if r == 200])
    too_many = len([r for r in results if r == 429])
    
    assert successes == 5
    assert too_many == 5

def test_v3_logging_with_duration():
    clear_modules()
    from v3_optimized.api_gateway import ApiGateway, Request, Response, LoggingFilter
    gw = ApiGateway()
    logger = LoggingFilter()
    gw.add_filter(logger)
    
    def slow_backend(req):
        time.sleep(0.1)
        return Response(200, {}, "OK")
        
    gw.register_backend("slow", slow_backend)
    gw.add_route("/api/slow", "slow")
    
    req = Request("/api/slow/test", "GET", {})
    gw.handle(req)
    
    assert len(logger.logs) == 1
    assert "GET /api/slow/test 200" in logger.logs[0]
    assert "s" in logger.logs[0]

def test_v3_circuit_breaker_exclude_own_rejections():
    clear_modules()
    from v3_optimized.api_gateway import ApiGateway, Request, Response, RateLimitFilter
    gw = ApiGateway()
    
    # Add a rate limit filter to simulate fast-fail
    gw.add_filter(RateLimitFilter(max_requests=1, window_sec=10))
    gw.register_backend("users", lambda req: Response(200, {}, "OK"))
    gw.add_route("/api", "users")
    
    req = Request("/api/test", "GET", {"Client-ID": "test"})
    
    # First request works
    assert gw.handle(req).status_code == 200
    
    # Next requests fail fast due to rate limit (429)
    assert gw.handle(req).status_code == 429
    assert gw.handle(req).status_code == 429
    assert gw.handle(req).status_code == 429
    assert gw.handle(req).status_code == 429
    
    # Circuit breaker should NOT open because 429 is from filter, not backend
    assert gw.circuit_breakers["users"].state == "CLOSED"
    assert gw.circuit_breakers["users"].failures == 0
