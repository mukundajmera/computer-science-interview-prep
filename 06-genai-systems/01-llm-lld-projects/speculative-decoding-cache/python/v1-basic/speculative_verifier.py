import random
from typing import List, Tuple

class SpeculativeDecodingVerifier:
    def __init__(self, k: int = 4):
        """
        Initializes the speculative decoding verifier.
        
        Args:
            k: The number of draft tokens generated in one step.
        """
        self.k = k
        self.accepted_tokens_count = 0
        self.target_evaluations = 0
        self.kv_cache_length = 0
        
    def generate_draft_tokens(self, vocab_size: int = 32000) -> Tuple[List[int], List[float]]:
        """
        Simulates the generation of K draft tokens along with their probabilities.
        
        Returns:
            Tuple of (draft_tokens, draft_probabilities)
        """
        tokens = [random.randint(0, vocab_size - 1) for _ in range(self.k)]
        # Simulate some probabilities
        probs = [random.uniform(0.1, 0.9) for _ in range(self.k)]
        return tokens, probs

    def calculate_acceptance_probability(self, p_target: float, p_draft: float) -> float:
        """
        Calculates the acceptance probability for a token.
        min(1, p_target(x) / p_draft(x))
        """
        if p_draft == 0.0:
            return 1.0 if p_target > 0.0 else 0.0
        return min(1.0, p_target / p_draft)
        
    def verify_step(
        self, 
        draft_tokens: List[int], 
        p_draft: List[float], 
        p_target: List[float],
        resample_token_id: int,
        fallback_token_id: int
    ) -> Tuple[List[int], int]:
        """
        Simulates the token acceptance/rejection loop.
        
        Args:
            draft_tokens: The list of K draft tokens.
            p_draft: The draft model probabilities for each token.
            p_target: The target model probabilities for each token.
            resample_token_id: The token ID to append if a rejection occurs and resampling is triggered.
            fallback_token_id: The token ID to append if all K tokens are accepted (the K+1 token).
            
        Returns:
            Tuple of (accepted_tokens, updated_kv_cache_length)
        """
        self.target_evaluations += 1
        accepted = []
        
        for i in range(len(draft_tokens)):
            pt = p_target[i]
            pd = p_draft[i]
            acc_prob = self.calculate_acceptance_probability(pt, pd)
            
            if random.random() <= acc_prob:
                accepted.append(draft_tokens[i])
                self.accepted_tokens_count += 1
            else:
                # Rejection triggers a resampling fallback
                # Append the resampled token instead of the rejected draft token
                accepted.append(resample_token_id)
                self.accepted_tokens_count += 1
                
                # Prefix reuse length increases by accepted tokens (including resampled)
                self.kv_cache_length += len(accepted)
                return accepted, self.kv_cache_length
                
        # All K draft tokens accepted
        # In speculative decoding, one extra token is generated from the target model's distribution
        accepted.append(fallback_token_id)
        self.accepted_tokens_count += 1
        
        self.kv_cache_length += len(accepted)
        return accepted, self.kv_cache_length

    def get_speedup_ratio(self) -> float:
        """
        Calculates the speedup ratio: accepted_tokens / target_evaluations.
        """
        if self.target_evaluations == 0:
            return 0.0
        return self.accepted_tokens_count / self.target_evaluations
