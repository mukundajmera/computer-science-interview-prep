import asyncio
import sys
import os
import unittest
from typing import AsyncGenerator, List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v1-basic")))
from streaming_server import LLMProvider, stream_response
sys.path.pop(0)


class FakeProvider(LLMProvider):
    def __init__(self, tokens: List[Tuple[str, float]], expected_tenant: str = None):
        self.tokens = tokens
        self.aborted = False
        self.expected_tenant = expected_tenant

    async def async_generate(self, prompt: str, tenant_id: str) -> AsyncGenerator[str, None]:
        if self.expected_tenant and tenant_id != self.expected_tenant:
            raise ValueError(f"Unauthorized tenant: {tenant_id}")
            
        for token, delay in self.tokens:
            if delay > 0:
                await asyncio.sleep(delay)
            yield token

    def abort(self) -> None:
        self.aborted = True


class TestStreamingServer(unittest.TestCase):
    """Test suite for the token streaming server."""
    def test_normal_trace(self):
        """Test normal successful SSE formatting."""
        async def _test():
            mock_tokens = [("Hel", 0.0), ("lo", 0.0), (" ", 0.0), ("world", 0.0)]
            provider = FakeProvider(mock_tokens)
            
            emitted_events = []
            async for event in stream_response(provider, "prompt", "tenant1"):
                emitted_events.append(event)
                
            self.assertIn("data: Hello \n\n", emitted_events)
            self.assertIn("data: world\n\n", emitted_events)
            self.assertIn("data: [DONE]\n\n", emitted_events)

        asyncio.run(_test())


    def test_cancellation_trace(self):
        """Test abort signal triggering on cancellation."""
        async def _test():
            mock_tokens = [("slow", 0.1)]
            provider = FakeProvider(mock_tokens)
            
            async def run_and_cancel():
                generator = stream_response(provider, "prompt", "tenant1")
                try:
                    task = asyncio.create_task(generator.__anext__())
                    await asyncio.sleep(0.01)
                    task.cancel()
                    await task
                except asyncio.CancelledError:
                    pass

            await run_and_cancel()
            self.assertTrue(provider.aborted)

        asyncio.run(_test())


    def test_heartbeat_injection(self):
        """Test heartbeat ping injection."""
        async def _test():
            class HeartbeatProvider(LLMProvider):
                def __init__(self):
                    self.aborted = False
                    
                async def async_generate(self, prompt: str, tenant_id: str) -> AsyncGenerator[str, None]:
                    await asyncio.sleep(100)
                    yield "never reached"
                    
                def abort(self):
                    pass
                    
            original_wait_for = asyncio.wait_for
            async def mock_wait_for(coro, timeout):
                if timeout == 15:
                    if not hasattr(mock_wait_for, "called"):
                        mock_wait_for.called = True
                        raise asyncio.TimeoutError()
                    else:
                        raise StopAsyncIteration()
                return await original_wait_for(coro, timeout)

            asyncio.wait_for = mock_wait_for
            
            try:
                provider = HeartbeatProvider()
                emitted_events = []
                async for event in stream_response(provider, "prompt", "tenant1"):
                    emitted_events.append(event)
                    
                self.assertIn("event: ping\ndata: {}\n\n", emitted_events)
            finally:
                asyncio.wait_for = original_wait_for

        asyncio.run(_test())


    def test_privacy_tenant_isolation(self):
        """Test privacy and tenant isolation."""
        async def _test():
            mock_tokens = [("secret", 0.0)]
            provider = FakeProvider(mock_tokens, expected_tenant="tenantA")
            
            emitted_events = []
            async for event in stream_response(provider, "prompt", "tenantA"):
                emitted_events.append(event)
                
            self.assertIn("data: secret\n\n", emitted_events)
            
            provider = FakeProvider(mock_tokens, expected_tenant="tenantB")
            emitted_events_fail = []
            async for event in stream_response(provider, "prompt", "tenantA"):
                emitted_events_fail.append(event)
                
            self.assertTrue(any('event: error' in e and 'Unauthorized tenant' in e for e in emitted_events_fail))

        asyncio.run(_test())


    def test_empty_input(self):
        """Test empty input handling."""
        async def _test():
            mock_tokens = []
            provider = FakeProvider(mock_tokens)
            emitted_events = []
            async for event in stream_response(provider, "prompt", "tenant1"):
                emitted_events.append(event)
            self.assertEqual(emitted_events, ["data: [DONE]\n\n"])
            
            mock_tokens = [("", 0.0), ("test", 0.0)]
            provider = FakeProvider(mock_tokens)
            emitted_events = []
            async for event in stream_response(provider, "prompt", "tenant1"):
                emitted_events.append(event)
            self.assertIn("data: test\n\n", emitted_events)

        asyncio.run(_test())


    def test_budget_boundaries(self):
        """Test budget boundary limits."""
        async def _test():
            mock_tokens = [("t1", 0.0), ("t2", 0.0), ("t3", 0.0)]
            provider = FakeProvider(mock_tokens)
            emitted_events = []
            async for event in stream_response(provider, "prompt", "tenant1", max_tokens=2):
                emitted_events.append(event)
                
            self.assertTrue(provider.aborted)
            self.assertIn('event: error\ndata: {"message": "Budget exceeded"}\n\n', emitted_events)
            self.assertIn("data: t1t2\n\n", emitted_events)
            self.assertIn("data: [DONE]\n\n", emitted_events)

        asyncio.run(_test())


if __name__ == '__main__':
    unittest.main()
