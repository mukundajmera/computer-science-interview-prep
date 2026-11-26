# Speculative Decoding: Common Pitfalls & Counterexamples

This document outlines scenarios where a Speculative Decoding implementation can fail structurally or regress in performance, distinguishing current base behavior from potential system extensions.

## 1. Misaligned Draft Model Vocabularies (Current Behavior)
**The Pitfall:** Selecting a draft model and a target model that do not share the exact same vocabulary or tokenizer schema.
**Counterexample:**
- **Target Model:** Llama 3 (128k token vocabulary).
- **Draft Model:** Llama 2 7B (32k token vocabulary).
- **Failure Trace:** The target model verifies a sequence of token IDs from the draft model. If the draft model produces token ID `31999`, the target model might interpret this as an entirely different subword string. The acceptance probability math relies on $p(x)$ meaning the probability of the exact same semantic token. An index mismatch invalidates the mathematical guarantee of distribution preservation and produces gibberish.

## 2. Low Acceptance Rate Causing Negative Speedup (Current Behavior)
**The Pitfall:** Assuming speculative decoding *always* provides a speedup regardless of model alignment.
**Counterexample:**
- **Scenario:** The target model is writing complex, novel source code. The draft model is a heavily compressed, generic conversational model with near-zero coding capability. 
- **Failure Trace:** Let $T_{draft}$ be the time to generate a draft token and $T_{target\_verify}$ be the parallel verification time. If the alignment is so poor that the first token is rejected 95% of the time, the effective output rate is roughly 1 token per pass (via the residual resample). The total latency per token becomes $K \times T_{draft} + T_{target\_verify}$. In standard decoding, latency is just $T_{target\_single}$. If $K \times T_{draft} + T_{target\_verify} > T_{target\_single}$, the system experiences a negative speedup—it is strictly slower than just running the large model.

## 3. GPU Memory Overhead and Batch Constraint (Current Behavior)
**The Pitfall:** Deploying speculative decoding without budgeting VRAM for the secondary model.
**Counterexample:**
- **Scenario:** A production server with an 80GB GPU runs a 70B int4-quantized target model taking up ~40GB VRAM.
- **Failure Trace:** The engineer attempts to load a 14B float16 draft model (requiring ~28GB) to maximize draft quality. The combined model weights consume 68GB of VRAM. This leaves only 12GB for the KV cache. Because batch sizes and context lengths directly map to KV cache size, the maximum concurrent batch size the server can handle is massively artificially constrained, leading to poor overall throughput despite the latency reduction on individual requests.

## 4. Discarding Viable Off-Path Extensions (Optional Extension)
**The Pitfall:** In a Medusa/EAGLE multi-head setup or Tree Attention (which are un-implemented advanced extensions in our current baseline), rejecting the *entire* drafted tree when a root node fails.
**Counterexample:**
- **Target Model:** A model processing a tree of drafted tokens, where a root node branches into node $A$ (Token 20) and independent parallel node $B$ (Token 30).
- **Failure Trace:** The target model rejects node $A$. If the linear verifier logic is incorrectly applied to the tree, it halts evaluation entirely and discards the valid parallel branch node $B$. A correct advanced tree verifier would reject $A$ but independently accept $B$ if $P_{accept}(B)$ passes, preserving the valid parallel speculation path.
