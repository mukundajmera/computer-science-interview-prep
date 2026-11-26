from dataclasses import dataclass, field
from typing import List, Optional, Dict
import re

@dataclass
class EvaluationSample:
    query: str
    contexts: List[str]
    answer: str
    ground_truth: Optional[str] = None

@dataclass
class EvaluationReport:
    context_relevance: float
    groundedness: float
    answer_relevance: float
    
@dataclass
class BatchReport:
    average_context_relevance: float
    average_groundedness: float
    average_answer_relevance: float
    total_samples: int
    
class RagEvaluator:
    def __init__(self):
        self._stop_words = {"the", "and", "for", "with", "that", "this", "are", "was", "has", "have", "not", "but", "from", "they", "its", "it", "is", "by"}
    
    def _extract_words(self, text: str) -> set:
        """Extract meaningful alphabetic words from text."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return set(w for w in words if w not in self._stop_words)

    def _extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple punctuation heuristics."""
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        return [s for s in sentences if len(s.strip()) > 0]

    def _compute_context_relevance(self, query: str, contexts: List[str]) -> float:
        query_words = self._extract_words(query)
        if not query_words:
            return 0.0
            
        combined_context = " ".join(contexts).lower()
        found = sum(1 for w in query_words if w in combined_context)
        return found / len(query_words)

    def _compute_groundedness(self, answer: str, contexts: List[str]) -> float:
        sentences = self._extract_sentences(answer)
        if not sentences:
            return 0.0
            
        combined_context = " ".join(contexts).lower()
        supported_sentences = 0
        valid_sentences = 0
        
        for sentence in sentences:
            sentence_words = self._extract_words(sentence)
            if not sentence_words:
                continue
            valid_sentences += 1
            found = sum(1 for w in sentence_words if w in combined_context)
            # Require > 50% match for better strictness in hallucination detection
            if found / len(sentence_words) > 0.5:
                supported_sentences += 1
                
        if valid_sentences == 0:
            return 0.0
        return supported_sentences / valid_sentences

    def _compute_answer_relevance(self, query: str, answer: str) -> float:
        query_words = self._extract_words(query)
        if not query_words:
            return 0.0
            
        answer_words = self._extract_words(answer)
        found = sum(1 for w in query_words if w in answer_words)
        return found / len(query_words)

    def evaluate_sample(self, query: str, contexts: List[str], answer: str, ground_truth: Optional[str] = None) -> EvaluationReport:
        context_relevance = self._compute_context_relevance(query, contexts)
        groundedness = self._compute_groundedness(answer, contexts)
        answer_relevance = self._compute_answer_relevance(query, answer)
        
        return EvaluationReport(
            context_relevance=context_relevance,
            groundedness=groundedness,
            answer_relevance=answer_relevance
        )

    def aggregate_batch(self, samples: List[EvaluationSample]) -> BatchReport:
        if not samples:
            return BatchReport(0.0, 0.0, 0.0, 0)
            
        total_cr = 0.0
        total_gr = 0.0
        total_ar = 0.0
        
        for sample in samples:
            report = self.evaluate_sample(
                sample.query,
                sample.contexts,
                sample.answer,
                sample.ground_truth
            )
            total_cr += report.context_relevance
            total_gr += report.groundedness
            total_ar += report.answer_relevance
            
        n = len(samples)
        return BatchReport(
            average_context_relevance=total_cr / n,
            average_groundedness=total_gr / n,
            average_answer_relevance=total_ar / n,
            total_samples=n
        )
