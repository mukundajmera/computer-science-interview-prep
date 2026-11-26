import pytest
import os
import sys
from unittest.mock import patch

# Adjust sys.path to load the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from speculative_verifier import SpeculativeDecodingVerifier

def test_exact_match_full_acceptance():
    verifier = SpeculativeDecodingVerifier(k=3)
    draft_tokens = [10, 20, 30]
    p_draft = [0.1, 0.2, 0.3]
    p_target = [0.2, 0.3, 0.4] # p_target > p_draft so min(1, p_target / p_draft) == 1
    
    # Even if random returns max float, it should accept since prob is 1.0
    with patch('random.random', return_value=0.99):
        accepted, kv_len = verifier.verify_step(
            draft_tokens=draft_tokens,
            p_draft=p_draft,
            p_target=p_target,
            resample_token_id=99,
            fallback_token_id=100
        )
        
    assert accepted == [10, 20, 30, 100]
    assert kv_len == 4
    assert verifier.accepted_tokens_count == 4
    assert verifier.target_evaluations == 1

def test_partial_rejection_and_resample():
    verifier = SpeculativeDecodingVerifier(k=3)
    draft_tokens = [10, 20, 30]
    p_draft = [0.5, 0.8, 0.5]
    p_target = [0.5, 0.2, 0.5]
    
    # Token 1: pt/pd = 1.0 -> accept
    # Token 2: pt/pd = 0.25 -> probability of acceptance is 0.25
    # Token 3: pt/pd = 1.0 -> accept
    
    # Let's mock random to accept first (random < 1.0), reject second (random > 0.25)
    with patch('random.random', side_effect=[0.5, 0.5]): # second is 0.5 > 0.25
        accepted, kv_len = verifier.verify_step(
            draft_tokens=draft_tokens,
            p_draft=p_draft,
            p_target=p_target,
            resample_token_id=99,
            fallback_token_id=100
        )
        
    assert accepted == [10, 99] # First accepted, second rejected and resampled
    assert kv_len == 2
    assert verifier.accepted_tokens_count == 2
    assert verifier.target_evaluations == 1

def test_speedup_calculation():
    verifier = SpeculativeDecodingVerifier(k=2)
    # Step 1: accept all + fallback -> 3 tokens generated in 1 eval
    p_draft = [0.1, 0.1]
    p_target = [0.2, 0.2]
    verifier.verify_step([10, 20], p_draft, p_target, 99, 100)
    
    # Step 2: reject first -> 1 token (resampled) in 1 eval
    p_draft = [0.8, 0.1]
    p_target = [0.1, 0.1]
    with patch('random.random', return_value=0.5): # 0.5 > 0.125
        verifier.verify_step([30, 40], p_draft, p_target, 99, 100)
        
    assert verifier.target_evaluations == 2
    assert verifier.accepted_tokens_count == 4 # 3 + 1
    assert verifier.get_speedup_ratio() == 2.0

def test_kv_cache_prefix_reuse():
    verifier = SpeculativeDecodingVerifier(k=3)
    
    # Initial state
    assert verifier.kv_cache_length == 0
    
    # Full acceptance
    verifier.verify_step([1, 2, 3], [0.1]*3, [0.2]*3, 99, 100)
    assert verifier.kv_cache_length == 4 # 3 draft + 1 fallback
    
    # Partial acceptance
    p_draft = [0.1, 0.9, 0.1]
    p_target = [0.2, 0.1, 0.2]
    # token 2 will be rejected if random > 0.111
    with patch('random.random', side_effect=[0.05, 0.5]):
        verifier.verify_step([4, 5, 6], p_draft, p_target, 99, 100)
    
    assert verifier.kv_cache_length == 6 # 4 from before + 1 accepted + 1 resampled
