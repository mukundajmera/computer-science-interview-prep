HEARTBEAT_TIMEOUT = 15

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Tuple, Set


class Clock(ABC):
    """Abstract interface to provide deterministic time."""
    @abstractmethod
    def time(self) -> float:
        pass


class LLMProvider(ABC):
    """Abstract interface for an LLM provider."""

    
    @abstractmethod
    async def async_generate(self, prompt: str, tenant_id: str) -> AsyncGenerator[str, None]:
        """Generates tokens asynchronously."""
        yield ""
        
    @abstractmethod
    def abort(self) -> None:
        """Cancels generation."""
        pass


class Tokenizer:
    """An approximation of a tokenizer."""
    @staticmethod
    def is_boundary(char: str) -> bool:
        # Simple string boundary checks: spaces or punctuation
        return char in {" ", ".", ",", "!", "?", ";", ":", "\n", "\t"}
        

async def stream_response(provider: LLMProvider, prompt: str, tenant_id: str, max_tokens: Optional[int] = None) -> AsyncGenerator[str, None]:
    """
    The Asynchronous Pipeline:
    Consumes an async token stream from an injected LLMProvider, processes and buffers
    the tokens, and yields formatted Server-Sent Events (SSE).
    
    Time Complexity: O(N) where N is the total number of yielded tokens.
    Space Complexity: O(M) where M is the maximum size of a semantic token chunk buffer.
    """
    chunk_buffer: Optional[str] = ""
    processed_token_count = 0
    
    # We must ensure that tokens generated are for this specific tenant_id.
    # The provider handles this internally, but we scope our variables here.
    
    generator = provider.async_generate(prompt, tenant_id)
    
    try:
        while True:
            try:
                # Wrap generation pull in asyncio.wait_for for heartbeat
                # Wait for the next token or timeout
                token = await asyncio.wait_for(generator.__anext__(), timeout=HEARTBEAT_TIMEOUT)
                
                # Check for empty input token
                if not token:
                    continue
                    
                processed_token_count += 1
                if max_tokens is not None and processed_token_count > max_tokens:
                    provider.abort()
                    yield 'event: error\ndata: {"message": "Budget exceeded"}\n\n'
                    break
                    
                chunk_buffer += token
                
                # Check buffer against our Tokenizer approximation
                if chunk_buffer and Tokenizer.is_boundary(chunk_buffer[-1]):
                    yield f"data: {chunk_buffer}\n\n"
                    chunk_buffer = ""
                    
            except asyncio.TimeoutError:
                # Emit heartbeat if we time out
                yield "event: ping\ndata: {}\n\n"
            except StopAsyncIteration:
                # End of generation stream
                break
                
        # Flushing remainder
        if chunk_buffer:
            yield f"data: {chunk_buffer}\n\n"
            
    except asyncio.CancelledError:
        # Client disconnect
        provider.abort()
        raise
    except Exception as e:
        # Provider exceptions
        yield f'event: error\ndata: {{"message": "{str(e)}"}}\n\n'
    finally:
        # Ephemeral State: The token buffer is strictly a local variable.
        # Clear structure aggressively for privacy boundaries.
        chunk_buffer = None
        generator = None
        
    # Final termination event
    yield "data: [DONE]\n\n"
