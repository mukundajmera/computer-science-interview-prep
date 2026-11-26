# Speculative Decoding: Design

## Distribution Preservation (Acceptance Criteria)

A fundamental tenet of Speculative Decoding is that the final sequence produced must be drawn from the exact same probability distribution as if it were generated solely by the target model. This is achieved through a specific mathematical acceptance criterion for each drafted token.

Given a draft token $x$ proposed by the draft model with probability $p_{draft}(x)$, and evaluated by the target model with probability $p_{target}(x)$, the acceptance probability is:

$$ P_{accept}(x) = \min\left(1, \frac{p_{target}(x)}{p_{draft}(x)}\right) $$

**Mathematical Proof of Preservation:**
When a token is accepted via this ratio, it guarantees that tokens overrepresented by the draft model are probabilistically down-sampled to match the target's distribution, while underrepresented tokens (or exactly matching probabilities) are always accepted. If a token is rejected, we perform **residual resampling** from the adjusted distribution $\max(0, p_{target}(x) - p_{draft}(x))$ to cover the probability mass the draft model missed. Our implementation simulates this by returning a `resample_token_id`.

## Verification Loop Algorithm

The `SpeculativeDecodingVerifier` implements the verification step where $K$ draft tokens are evaluated in parallel. The algorithm within `verify_step(draft_tokens, p_draft, p_target, resample_token_id, fallback_token_id)` works as follows:

1. Iterate over the $K$ `draft_tokens` sequentially.
2. For each token at index $i$, calculate `acc_prob = min(1.0, p_target[i] / p_draft[i])`.
3. Draw a random number from a uniform distribution $[0, 1]$.
4. **Acceptance**: If `random <= acc_prob`:
   - Append the draft token to the `accepted` list.
   - Increment `accepted_tokens_count`.
5. **Rejection**: If `random > acc_prob`:
   - Reject the current draft token.
   - Append the `resample_token_id` to the `accepted` list. (This simulates drawing from the residual distribution).
   - Increment `accepted_tokens_count`.
   - Update KV cache length by adding `len(accepted)`.
   - Halt verification for remaining tokens and return early.
6. **Full Acceptance Fallback**: If all $K$ tokens are accepted, append the `fallback_token_id` to `accepted` (simulating the single additional token generated from the target distribution natively in this forward pass). Update KV cache and return.

[Speculative Loop Diagram](diagrams/speculative-loop.mmd)

## Hand-Checked Normal/Error Fixture

From the implementation's test suite (`test_partial_rejection_and_resample`), we can observe a partial rejection boundary case:
- **Given:** $K=3$. Draft tokens `[10, 20, 30]`. 
- **Probabilities:** $P_{draft} = [0.5, 0.8, 0.5]$ and $P_{target} = [0.5, 0.2, 0.5]$.
- **Execution Trace:**
  - Token `10`: $P_{target} / P_{draft} = 0.5 / 0.5 = 1.0$. Always accepted.
  - Token `20`: $P_{target} / P_{draft} = 0.2 / 0.8 = 0.25$. 
  - If the random uniform sample $> 0.25$, Token `20` is **rejected**.
- **Result:** The system immediately halts evaluation for the 3rd token. It appends the accepted token `10` and immediately appends a fallback `resample_token_id` (e.g., `99`) in place of `20`. The final accepted list is `[10, 99]`, and the sequence's KV cache length increases by 2. Target evaluations increment by 1.

## KV Cache Prefix Reuse Logic

Because the target model evaluates all $K$ draft tokens in parallel, we must maintain a continuous and consistent KV cache. The verifier tracks the active context length in `self.kv_cache_length`.

When tokens are accepted, the KV cache length grows by the total number of accepted tokens (which includes either the final resampled token upon rejection or the `fallback_token_id` upon full acceptance). The design implicitly handles prefix reuse: any accepted tokens become part of the persistent KV cache prefix for the next iteration. If a rejection occurs at index $i$, tokens $i+1$ to $K$ are discarded, and their hypothetical KV cache entries are never finalized, ensuring the engine resumes exactly from the valid prefix length.

## Speedup Ratio Formulation

The theoretical efficiency of the system is tracked via the speedup ratio, formulated as:

$$ \text{Speedup Ratio} = \frac{\text{accepted\_tokens\_count}}{\text{target\_evaluations}} $$

Where `accepted_tokens_count` encompasses all drafted tokens that pass the criteria, plus the resampled or fallback tokens.
`target_evaluations` increments by exactly $1$ per call to `verify_step`, representing the single large model forward pass.

## Public API Mapping

The described behavior maps exactly to the actual implemented `SpeculativeDecodingVerifier` public API:
- `__init__(self, k: int = 4)`
- `generate_draft_tokens(self, vocab_size: int = 32000) -> Tuple[List[int], List[float]]`
- `calculate_acceptance_probability(self, p_target: float, p_draft: float) -> float`
- `verify_step(self, draft_tokens: List[int], p_draft: List[float], p_target: List[float], resample_token_id: int, fallback_token_id: int) -> Tuple[List[int], int]`
- `get_speedup_ratio(self) -> float`

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

## Algorithm Complexity

- **Time Complexity:** $O(K)$ per verification step, where $K$ is the number of drafted tokens.
- **Space Complexity:** $O(K)$ for storing the `accepted` tokens list and caching the intermediate results up to sequence length $K$.

## Limitations and Privacy Boundaries

- **VRAM Overhead Simulation:** The implementation simulates KV cache bounds but does not represent actual VRAM allocations. It is an algorithmic simulator, not a production engine.
- **Context Isolation:** Sequence generation assumes continuous valid sequence length and does not account for independent batch isolation privacy boundaries.
