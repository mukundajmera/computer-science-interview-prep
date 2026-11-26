# Speculative Decoding: Approach

## Draft Model Selection

The success of speculative decoding depends heavily on the drafting mechanism's speed and alignment with the target model.
There are multiple approaches to generating the draft tokens:

1.  **Small Sibling Model:** Using a significantly smaller model from the same family (e.g., drafted by Llama 2 7B for a target of Llama 2 70B). The small model is fast and shares a similar distribution, often leading to a high acceptance rate. This is the standard approach assumed in our basic implementation simulator.
2.  **N-Gram or Retrieval Matching (Unimplemented Extension):** Generating drafts based on matching $N$-grams from the prompt or retrieved context. This is highly efficient and requires no neural network drafting, but relies entirely on exact matches and has zero generalization.
3.  **Self-Speculative (e.g., Medusa, EAGLE) (Unimplemented Extension):** Instead of a separate model, additional projection heads are added to the target model to predict multiple future tokens simultaneously during a single forward pass. This removes the need for two separate models to reside in VRAM.

## Acceptance Criterion Implementation

The `calculate_acceptance_probability(p_target, p_draft)` method implements the core stochastic acceptance check:
$$ P_{accept}(x) = \min\left(1, \frac{p_{target}(x)}{p_{draft}(x)}\right) $$
In the case where the draft model assigns $0.0$ probability to a token, the implementation returns $1.0$ if the target probability is greater than $0.0$, and $0.0$ otherwise, preventing division by zero errors.

During `verify_step`, the algorithm generates a uniform random number. If `random <= P_accept`, the token is appended to the accepted output. If `random > P_accept`, the token is rejected. This rejection stops the evaluation of the remaining $K-i$ draft tokens for the current step, as the context prefix is no longer valid. The algorithm then simulates drawing from the adjusted residual distribution by appending the provided `resample_token_id`.

## Actual Public APIs

- `__init__(self, k: int = 4)`
- `generate_draft_tokens(self, vocab_size: int = 32000) -> Tuple[List[int], List[float]]`
- `calculate_acceptance_probability(self, p_target: float, p_draft: float) -> float`
- `verify_step(self, draft_tokens: List[int], p_draft: List[float], p_target: List[float], resample_token_id: int, fallback_token_id: int) -> Tuple[List[int], int]`
- `get_speedup_ratio(self) -> float`

## Hand-Checked Normal/Error Fixture

From the test suite (`test_partial_rejection_and_resample`), here is a boundary case showing partial rejection:
- **Given:** $K=3$. Draft tokens `[10, 20, 30]`. 
- **Probabilities:** $P_{draft} = [0.5, 0.8, 0.5]$ and $P_{target} = [0.5, 0.2, 0.5]$.
- **Execution Trace:**
  - Token `10`: $P_{target} / P_{draft} = 0.5 / 0.5 = 1.0$. Always accepted.
  - Token `20`: $P_{target} / P_{draft} = 0.2 / 0.8 = 0.25$. 
  - If the random uniform sample $> 0.25$, Token `20` is **rejected**.
- **Result:** Evaluation halts immediately for the 3rd token. It appends the accepted token `10` and immediately appends a fallback `resample_token_id` (e.g., `99`) in place of `20`. The final accepted list is `[10, 99]`, and the sequence's KV cache length increases by 2. Target evaluations increment by 1.

## Algorithm Names and Complexity

The actual implementation models the `SpeculativeDecodingVerifier` with strict constraints.
- **Verification Loop Complexity:** The algorithm runs in $O(K)$ time per step, where $K$ is the number of drafted tokens, since it iterates over the sequence linearly and stops upon rejection.
- **Space Complexity:** The algorithm requires $O(K)$ space to store probabilities and intermediate token lists. 

## Expected Tokens Per Forward Pass

The expected tokens generated per forward pass (the target evaluation) depends entirely on the alignment between the draft and target models.

-   **Worst Case (Total Misalignment):** If the first draft token is consistently rejected, $0$ draft tokens are accepted. However, because we sample from the residual distribution (or evaluate the target natively), $1$ token (the `resample_token_id`) is generated. Expected tokens per pass = $1$. Speedup = $1.0\times$ (no gain).
-   **Best Case (Total Alignment):** If all $K$ draft tokens are accepted, the target model's final evaluation provides the distribution for the $K+1$ token natively. Expected tokens per pass = $K+1$. Speedup = $(K+1)\times$.
-   **Average Case:** In practice, with a well-aligned small sibling model (e.g., $K=4$), empirical results often yield an acceptance rate that results in $2$ to $3$ tokens generated per pass, equating to a $2.0\times$ to $3.0\times$ wall-clock speedup for the user, assuming the draft generation time is negligible compared to the target verification. Our `get_speedup_ratio()` dynamically calculates this exact ratio across the lifespan of the `SpeculativeDecodingVerifier`.

## Limitations and Privacy Boundaries

**Limitations:**
- **VRAM Overhead:** Running two distinct models concurrently (the small sibling draft and the large target) inherently increases the minimum GPU VRAM required, potentially limiting batch sizes compared to running the target model alone. It is an algorithmic simulator, not a production engine.
- **Negative Speedup Risk:** If the draft model is severely misaligned (e.g., due to different tokenizers or vastly different training distributions), the acceptance rate can drop so low that the overhead of drafting and scoring actually increases total wall-clock latency compared to standard autoregressive decoding.

**Privacy Boundaries:**
- **Context Isolation:** The KV Cache length tracking (`self.kv_cache_length`) operates on a strictly per-sequence basis. In a production engine, speculative drafted tokens and their corresponding KV entries must be strongly isolated across different user sessions to prevent prompt or completion leakage. This simulator tracks single-sequence length explicitly.
- **Draft Model Data Security:** The draft model must have the exact same security classification as the target model. Because it proposes the tokens that the target model evaluates, any prompt injections or sensitive data exposed to the target must also be considered exposed to the drafting mechanism.
