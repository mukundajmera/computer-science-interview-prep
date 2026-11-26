import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from rag_evaluator import RagEvaluator, EvaluationSample

def test_context_relevance_metric():
    evaluator = RagEvaluator()
    # Query words: how, tall, eiffel, tower
    # Assuming 'how' is stopped, 'tall', 'eiffel', 'tower' are keywords
    query = "How tall is the Eiffel Tower?"
    contexts_good = ["The Eiffel Tower is 330 meters tall."]
    contexts_bad = ["The Statue of Liberty is in New York."]
    
    report_good = evaluator.evaluate_sample(query, contexts_good, "")
    report_bad = evaluator.evaluate_sample(query, contexts_bad, "")
    
    assert report_good.context_relevance > report_bad.context_relevance

def test_groundedness_hallucination_detection():
    evaluator = RagEvaluator()
    # Sentences are evaluated for support.
    answer_good = "The Eiffel Tower is 330 meters tall."
    answer_hallucinated = "The Eiffel Tower is 330 meters tall. It was built by aliens."
    contexts = ["The Eiffel Tower is 330 meters tall. It was built by Gustave Eiffel."]
    
    report_good = evaluator.evaluate_sample("", contexts, answer_good)
    report_hallucinated = evaluator.evaluate_sample("", contexts, answer_hallucinated)
    
    assert report_good.groundedness == 1.0
    assert report_hallucinated.groundedness < 1.0

def test_answer_relevance_metric():
    evaluator = RagEvaluator()
    query = "Where is the Eiffel Tower?"
    answer_relevant = "The Eiffel Tower is in Paris."
    answer_irrelevant = "The weather is nice today."
    
    report_relevant = evaluator.evaluate_sample(query, [], answer_relevant)
    report_irrelevant = evaluator.evaluate_sample(query, [], answer_irrelevant)
    
    assert report_relevant.answer_relevance > report_irrelevant.answer_relevance

def test_batch_report_aggregation():
    evaluator = RagEvaluator()
    samples = [
        EvaluationSample(
            query="Where is Paris?",
            contexts=["Paris is in France."],
            answer="Paris is in France."
        ),
        EvaluationSample(
            query="What is 2+2?",
            contexts=[],
            answer="2+2 is 4."
        )
    ]
    
    batch_report = evaluator.aggregate_batch(samples)
    
    assert batch_report.total_samples == 2
    assert batch_report.average_context_relevance >= 0.0
    assert batch_report.average_groundedness >= 0.0
    assert batch_report.average_answer_relevance >= 0.0
    
    # Test empty batch
    empty_report = evaluator.aggregate_batch([])
    assert empty_report.total_samples == 0
    assert empty_report.average_context_relevance == 0.0
