# Speculative Decoding: Advanced Follow-Ups

Once the core sequential Speculative Decoding algorithm (the Mandatory Interview Baseline) is implemented and understood, interviewers will often push for architectural extensions that increase the expected value of generated tokens per forward pass. **Note: These are Optional Staff Follow-ups not present in the current baseline implementation, and implementing them is explicitly optional.**

## 1. Tree-Based Speculative Decoding (Speculative Tree Attention)
**The Concept:** Instead of drafting a single linear sequence of $K$ tokens, the draft model generates a tree of possible token paths (e.g., $N$ possible branches). The target model then verifies all paths simultaneously.
**Mechanics:**
-   To verify a tree in a single forward pass, the system uses a specialized 2D attention mask (Tree Attention) so that tokens in one branch do not attend to tokens in a mutually exclusive sibling branch.
-   **Why it's better:** In linear speculative decoding, if token $i$ is rejected, tokens $i+1 \dots K$ are entirely discarded, capping the speedup. With a tree, a rejection on one branch does not invalidate alternative parallel branches drafted from the same root. This dramatically increases the probability of finding a long accepted sequence in highly stochastic text generation.

## 2. Speculative Streaming 
**The Concept:** Integrating speculative decoding within a streaming API where partial outputs must be returned to the client in real-time.
**Mechanics:**
-   Because speculative decoding generates tokens in "chunks" (e.g., yielding 1 to $K+1$ tokens unpredictably per forward pass), the cadence of the stream becomes "bursty" rather than a steady character-by-character flow.
-   A system design must buffer or smoothly interpolate these chunks in the presentation layer (frontend) or carefully manage the network flush intervals so that the bursty output doesn't cause UI stuttering or timeout errors on the client side. 

## 3. Speculative Sampling with Temperature > 0
**The Concept:** Our mathematical proof of distribution preservation holds true, but the dynamics of acceptance change wildly depending on the sampling temperature applied to the model logits.
**Mechanics:**
-   **Temperature = 0 (Greedy):** The acceptance probability simplifies to exact matching. If the draft model's `argmax` matches the target model's `argmax`, it is accepted; otherwise, it is rejected.
-   **Temperature > 0 (Stochastic):** The distributions $p_{draft}$ and $p_{target}$ are flattened. This can actually *increase* the acceptance rate of "imperfect" drafts because the target model assigns a non-zero probability to a wider array of tokens, making the ratio $p_{target} / p_{draft}$ higher and more likely to pass the $random \le P_{accept}$ threshold. Candidates should be able to discuss how higher temperature modifies the threshold math in favor of broader acceptance.
