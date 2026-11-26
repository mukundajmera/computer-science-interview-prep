import unittest
import sys
import os

# Add v1-basic to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))

from api_gateway_simulator import ApiGatewaySimulator, Request

class TestApiGatewaySimulator(unittest.TestCase):
    def test_normal_trace(self):
        gateway = ApiGatewaySimulator()
        headers = {"Authorization": "Bearer valid-token"}
        req = Request("/api/v1/data", headers)
        
        res = gateway.handle_request(req)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, "OK from downstream")

    def test_failure_trace(self):
        gateway = ApiGatewaySimulator()
        headers = {"Authorization": "Bearer valid-token"}
        req = Request("/api/v1/data", headers)
        
        # Simulate repeated timeouts by tripping the breaker
        gateway.circuit_breaker.trip_open()
        
        # Next request should fail fast with 503
        res = gateway.handle_request(req)
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.body, "Service Unavailable")

if __name__ == '__main__':
    unittest.main()
