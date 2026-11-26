import time
import base64
from typing import Dict, List, Optional, Generator

class TenantConfig:
    def __init__(self, tenant_id: str, tier: str, system_prompt: str, max_tokens_per_minute: int):
        self.tenant_id = tenant_id
        self.tier = tier # e.g., 'Basic', 'Pro', 'Enterprise'
        self.system_prompt = system_prompt
        self.max_tokens_per_minute = max_tokens_per_minute
        self.encryption_key = f"secret-key-{tenant_id}"

class TokenRateLimiter:
    def __init__(self):
        # tenant_id -> {"tokens": int, "reset_time": float}
        self.usage: Dict[str, Dict[str, float]] = {}

    def check_and_consume(self, tenant_id: str, tokens: int, limit: int) -> bool:
        now = time.time()
        if tenant_id not in self.usage:
            self.usage[tenant_id] = {"tokens": 0, "reset_time": now + 60.0}

        # Reset if minute has passed
        if now >= self.usage[tenant_id]["reset_time"]:
            self.usage[tenant_id] = {"tokens": 0, "reset_time": now + 60.0}

        if self.usage[tenant_id]["tokens"] + tokens > limit:
            return False

        self.usage[tenant_id]["tokens"] += tokens
        return True

class SessionState:
    def __init__(self, session_id: str, max_history: int = 10):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history
        self.last_accessed = time.time()

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history.pop(0)
        self.last_accessed = time.time()

class MultiTenantChatAssistant:
    def __init__(self, max_active_sessions: int = 100):
        self.tenants: Dict[str, TenantConfig] = {}
        # tenant_id -> session_id -> SessionState
        self.sessions: Dict[str, Dict[str, SessionState]] = {}
        self.rate_limiter = TokenRateLimiter()
        self.max_active_sessions = max_active_sessions

    def register_tenant(self, config: TenantConfig):
        self.tenants[config.tenant_id] = config
        self.sessions[config.tenant_id] = {}

    def _encrypt(self, text: str, key: str) -> str:
        # Simplified encryption simulation
        combined = f"{key}:{text}"
        return base64.b64encode(combined.encode()).decode()

    def _decrypt(self, encrypted_text: str, key: str) -> str:
        # Simplified decryption simulation
        try:
            decoded = base64.b64decode(encrypted_text.encode()).decode()
            prefix = f"{key}:"
            if decoded.startswith(prefix):
                return decoded[len(prefix):]
            return encrypted_text # fallback
        except Exception:
            return encrypted_text

    def _evict_stale_sessions_if_needed(self, tenant_id: str):
        tenant_sessions = self.sessions.get(tenant_id, {})
        if len(tenant_sessions) >= self.max_active_sessions:
            # Evict LRU session
            oldest_session_id = min(tenant_sessions.keys(), key=lambda k: tenant_sessions[k].last_accessed)
            del tenant_sessions[oldest_session_id]

    def chat_stream(self, tenant_id: str, session_id: str, message: str) -> Generator[str, None, None]:
        if tenant_id not in self.tenants:
            yield "Error: Tenant not found"
            return

        config = self.tenants[tenant_id]

        # Estimate input tokens (simple word count)
        input_tokens = len(message.split())

        # Simple rate limit check for input tokens
        if not self.rate_limiter.check_and_consume(tenant_id, input_tokens, config.max_tokens_per_minute):
            yield "Error: Rate limit exceeded"
            return

        # Session management
        if session_id not in self.sessions[tenant_id]:
            self._evict_stale_sessions_if_needed(tenant_id)
            self.sessions[tenant_id][session_id] = SessionState(session_id)

        session = self.sessions[tenant_id][session_id]

        # Encrypt and store user message
        encrypted_msg = self._encrypt(message, config.encryption_key)
        session.add_message("user", encrypted_msg)

        # Build prompt context
        decrypted_history = []
        for msg in session.history:
            decrypted_content = self._decrypt(msg["content"], config.encryption_key)
            decrypted_history.append(f"{msg['role']}: {decrypted_content}")

        context = f"System: {config.system_prompt}\n" + "\n".join(decrypted_history)

        # Simulated LLM generation based on input
        response_text = f"Assistant response for tier {config.tier} to: '{message}'. Context len: {len(context)}"
        output_tokens_estimated = len(response_text.split())

        # Check rate limit for estimated output
        if not self.rate_limiter.check_and_consume(tenant_id, output_tokens_estimated, config.max_tokens_per_minute):
             yield "Error: Rate limit exceeded during generation"
             return

        # Streaming chunking simulation
        words = response_text.split(" ")
        for word in words:
            yield word + " "

        # Encrypt and store assistant message
        encrypted_response = self._encrypt(response_text, config.encryption_key)
        session.add_message("assistant", encrypted_response)
