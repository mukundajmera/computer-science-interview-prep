# Speculative Decoding: The Problem Space

## Assigned Requirements

- Implement a basic Speculative Decoding verifier (`SpeculativeDecodingVerifier`) focusing purely on the token acceptance loop.
- Expose a `generate_draft_tokens` method to simulate drafting $K$ tokens.
- Expose a `calculate_acceptance_probability` to return the appropriate stochastic boundary for each token.
- Expose a `verify_step` method to simulate evaluating the $K$ drafts, simulating random rejection against the target distribution, and updating the KV cache state context length per sequence.
- Expose a `get_speedup_ratio` method computing the efficiency of the cache.
- Do not implement actual LLM inference frameworks or tensor ops; use standard libraries.

## The Inference Memory Bandwidth Bottleneck

Large Language Model (LLM) inference, particularly during the generation phase (autoregressive decoding), is heavily bottlenecked by memory bandwidth rather than compute. 
To generate a single token, the engine must load the entire model's weights from GPU VRAM into the streaming multiprocessors (SM) and compute the forward pass to produce the next logit.
For a modern model like Llama 2 70B, which requires reading ~140GB of weights per token generation step, the compute logic is extremely fast, but the memory fetching takes the majority of the latency budget. 
This results in poor GPU utilization and a low operational arithmetic intensity, classifying the autoregressive generation as severely memory-bound.

## Autoregressive Decoding Latency

In standard autoregressive decoding, tokens are generated strictly one by one. The total latency for generating $N$ tokens is directly proportional to $N$ sequential forward passes of the target model:
$$ Latency = N \times T_{target} $$
Where $T_{target}$ is the latency of a single forward pass of the target model. 

Since $T_{target}$ is constrained by the memory bandwidth required to load the parameters, accelerating token generation latency for a single user request fundamentally requires a shift in how we perform these forward passes. Batching requests helps with throughput (using the same loaded weights for multiple sequences), but it does not improve the inter-token latency for an individual user prompt.

## The Speculative Decoding Objective

The objective of **Speculative Decoding** is to significantly reduce the inter-token latency of LLM inference without altering the target model's output distribution.

Instead of generating tokens one by one with the large target model, we use a much smaller, faster *draft* model to generate a sequence of $K$ speculative tokens quickly. The target model then verifies these $K$ draft tokens in a **single parallel forward pass**.

Because evaluating $K$ tokens in parallel utilizes the same memory bandwidth (reading the target model weights once) as generating a single token, the target model essentially "scores" the draft for free.

If the draft model's predictions align with the target model's distribution, the target model accepts the tokens, effectively generating multiple tokens in the time it usually takes to generate just one. The crucial requirement of this technique is that the final output distribution must precisely match the distribution of the target model alone, ensuring mathematically equivalent output quality while drastically lowering latency.

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
- **Space Complexity:** $O(K)$ for storing the `accepted` tokens list and intermediate results up to sequence length $K$.

## Limitations and Privacy Boundaries

- **VRAM Overhead Simulation:** The implementation simulates KV cache bounds but does not represent actual VRAM allocations. It is an algorithmic simulator, not a production engine.
- **Context Isolation:** Sequence generation assumes continuous valid sequence length and does not account for independent batch isolation privacy boundaries.
