# System Design: LLM Evaluation & Benchmark Platform

## 1. High-Level Architecture

The platform acts as a central control plane for GenAI quality, orchestrating asynchronous evaluation jobs, managing test data, and surfacing insights.

### Component Architecture

[Architecture Diagram](diagrams/eval-architecture.mmd)

## 2. Core Components & Deep Dives

### 2.1 Golden Test Set Registry & Synthetic Generation
* **Registry:** Stores versioned datasets containing inputs, expected outputs (optional), and context. This registry technically enforces:
    * **Provenance and Versioning:** Every dataset is immutably versioned, with metadata tracking the origin (e.g., synthetic generation source, human annotator, production sampled logs).
    * **Golden-Set Splits:** Data is explicitly partitioned into training, validation, and test splits to evaluate generalization and prevent overfitting.
    * **Leakage Controls & Tenant Privacy:** Stringent isolation boundaries and cryptographic hashing are applied to prevent test set contamination into model training pipelines and to ensure strict tenant privacy, isolating data between distinct enterprise customers or organizational units.
* **Synthetic Generation (Evol-Instruct):** To prevent models from overfitting to static test sets, the platform uses an LLM to dynamically generate new, complex test cases. It takes a simple seed prompt (e.g., "Write a python script to sort an array") and mutates it (e.g., "Write a python script to sort an array using a custom comparator, ensuring O(N log N) time complexity, and handle edge cases with None values").

### 2.2 LLM-as-a-Judge Engine
Using a strong LLM (e.g., GPT-4) to evaluate the outputs of weaker or cheaper target models. Note: LLM judges are probabilistic and fallible.

* **Position Bias Mitigation & Random Seed Controls:** LLMs often favor the first response they see. The orchestrator mitigates this via strict pair-order swapping (running two evaluations for A/B comparisons: one where Model A is first, one where Model B is first) and by varying random seeds. *Note: Position swaps and voting mitigate specific biases but do not prove correctness.*
* **Self-Consistency Voting:** For critical evaluations, the orchestrator queries the judge model with a non-zero temperature multiple times (e.g., 5 times) and takes the majority vote to ensure a robust evaluation. (Like position swaps, voting mitigates specific biases but does not prove correctness).
* **Judge/Human Disagreement Example:** To handle uncertainty, the system tracks agreement rates between LLM judges and human annotators. For instance, on a 5-item evaluation list, if the LLM judge outputs `[Pass, Fail, Pass, Pass, Fail]` and the human annotator outputs `[Pass, Pass, Pass, Pass, Fail]`, the system calculates a disagreement on index 1, yielding an 80% agreement score (4/5). Thresholds determine whether the evaluation is accepted or flagged for further human review.

### 2.3 RAG Triad Evaluators
For evaluating Retrieval-Augmented Generation (RAG) pipelines, the platform implements specific metrics without needing golden answers:
1. **Context Precision:** Did the retriever fetch relevant context for the query? (Evaluates Retriever).
2. **Faithfulness:** Is the generated answer grounded *strictly* in the retrieved context, or did it hallucinate? (Evaluates Generator).
3. **Answer Relevance:** Does the final answer actually address the user's original query? (Evaluates Generator).

### 2.4 ELO Rating Tournament Engine
To continuously benchmark models:
* Deployed models are entered into a tournament.
* The engine samples test prompts and asks two random models for responses.
* The LLM-as-a-Judge determines the winner.
* ELO ratings are updated continuously, providing a live leaderboard of model capabilities, ensuring regressions are caught over time.

### 2.5 Online Traffic Sampling & Safety Monitoring
* Production applications asynchronously log 5% of traffic to a Kafka topic.
* Workers pull from this queue and run lightweight safety classifiers and hallucination detectors.
* If a spike in safety violations (e.g., successful jailbreaks) is detected, alerts are fired.

### 2.6 CI/CD Quality Gates
Integrated into the CI/CD pipeline, these gates evaluate the release readiness of models and prompts:
* **Evaluation Costs & Limits:** Quality gates explicitly state the token and latency costs of running the evaluation suite, enforcing budget constraints.
* **Uncertainty & Abstention:** Evaluators support abstention (the model outputting "I don't know" or "Uncertain"). High rates of abstention or low confidence scores automatically pause deployments.
* **Human Escalation Paths:** When uncertainty thresholds are breached or safety evaluations flag potential severe regressions, the gate blocks deployment and automatically routes the evaluation artifacts (logs, prompts, responses) to a human reviewer for manual escalation and approval.

## 3. Data Model

**Table: TestSets**
* `id` (UUID)
* `name` (String)
* `version` (Int)
* `type` (Enum: QA, Adversarial, RAG)

**Table: Evaluations**
* `id` (UUID)
* `test_case_id` (UUID)
* `target_model_id` (String)
* `judge_model_id` (String)
* `score` (Float)
* `rationale` (Text)
* `timestamp` (DateTime)

**Table: EloRatings**
* `model_id` (String)
* `current_elo` (Int)
* `matches_played` (Int)
* `last_updated` (DateTime)

## 4. API Design

`POST /api/v1/evaluations/trigger`
Triggers a CI/CD evaluation run.
```json
{
  "target_model": "llama-3-8b-custom",
  "test_set_id": "ts-12345",
  "metrics": ["faithfulness", "toxicity", "helpfulness"],
  "judge_model": "gpt-4o"
}
```

`GET /api/v1/leaderboard`
Fetches the current ELO ratings of all tracked models.

## 5. Trade-offs & Design Decisions

### LLM-as-a-Judge vs. Traditional Metrics (ROUGE/BLEU)
* **Decision:** Prioritize LLM-as-a-Judge.
* **Trade-off:** Traditional metrics are fast and cheap but fail to capture semantic meaning and nuance. LLM judges are expensive and slow but correlate highly with human judgment. We mitigate cost by caching evaluations and using smaller models (e.g., Llama-3-70B) for simpler routing tasks.

### Synchronous vs. Asynchronous Evaluation
* **Decision:** Strictly Asynchronous.
* **Trade-off:** We cannot block CI/CD pipelines for hours while large test sets run. The API returns a job ID, and CI/CD polls or waits for a webhook. Similarly, production sampling must never add latency to user requests.

### Stateful vs. Stateless Workers
* **Decision:** Stateless workers pulling from message queues.
* **Trade-off:** Ensures high availability and horizontal scalability. If a judge API rate-limits us, the worker can simply NACK the message and retry later with exponential backoff.

## 6. Implementation Contracts

### Golden-Set Splits, Contamination, and Evaluation Controls

The following code snippets demonstrate how to implement dataset partitioning, tenant privacy through cryptographic hashing of inputs (to prevent data contamination), pair-order position swaps (randomizing the order to mitigate positional bias), and self-consistency voting with a judge/human disagreement worked score example.

**Java Implementation:**
```java
import java.security.MessageDigest;
import java.util.*;

public class EvaluationEngine {
    
    // Quality Gates Constants
    private static final double MAX_COST_USD = 1.00;
    private static final double UNCERTAINTY_THRESHOLD = 0.7; // Needs > 70% confidence
    
    public enum EvaluationSplit {
        TRAIN, VALIDATION, TEST
    }

    public static class DatasetItem {
        public String tenantId;
        public String prompt;
        public String expectedAnswer;
        public EvaluationSplit split;
        
        public DatasetItem(String tenantId, String prompt, String expectedAnswer, EvaluationSplit split) {
            this.tenantId = tenantId;
            this.prompt = prompt;
            this.expectedAnswer = expectedAnswer;
            this.split = split;
        }
    }

    // 1. Tenant Privacy and Leakage Control via Hashing
    public static String hashForPrivacy(String tenantId, String text) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            String combined = tenantId + ":" + text;
            byte[] hash = md.digest(combined.getBytes("UTF-8"));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    // 2. Position Swaps & Random Seed Controls (Mitigate specific biases but do not prove correctness)
    public static List<String> prepareSwappedPrompts(String modelA, String modelB, long seed) {
        Random random = new Random(seed);
        List<String> prompts = new ArrayList<>();
        // Standard order
        prompts.add("Compare Model A: " + modelA + " vs Model B: " + modelB);
        // Swapped order
        prompts.add("Compare Model A: " + modelB + " vs Model B: " + modelA);
        
        // Randomly shuffle to further mitigate position bias
        if (random.nextBoolean()) {
            Collections.reverse(prompts);
        }
        return prompts;
    }
    
    // 3. Judge/Human Disagreement Worked Score Example
    public static double calculateAgreementScore(List<Boolean> judgePassFail, List<Boolean> humanPassFail) {
        int judgeSize = judgePassFail.size();
        int humanSize = humanPassFail.size();
        if (judgeSize != humanSize || judgePassFail.isEmpty()) {
            return 0.0;
        }
        int matches = 0;
        for (int i = 0; i < judgeSize; i++) {
            if (judgePassFail.get(i).equals(humanPassFail.get(i))) {
                matches++;
            }
        }
        return (double) matches / judgeSize;
    }
    
    // 4. Quality Gates
    public static boolean evaluateQualityGate(double costUsd, double confidenceScore, boolean didAbstain) {
        if (costUsd > MAX_COST_USD) {
            System.out.println("Blocked: Evaluation cost exceeded budget.");
            return false;
        }
        if (didAbstain) {
             System.out.println("Blocked: Judge model abstained from evaluation. Escalating to human.");
             return false;
        }
        if (confidenceScore < UNCERTAINTY_THRESHOLD) {
             System.out.println("Blocked: High uncertainty detected. Escalating to human.");
             return false;
        }
        System.out.println("Gate Passed.");
        return true;
    }

    public static void main(String[] args) {
        DatasetItem item = new DatasetItem("tenant_99", "Explain gravity.", "A force of attraction...", EvaluationSplit.TEST);
        System.out.println("Private Hash: " + hashForPrivacy(item.tenantId, item.prompt));
        
        List<String> evalTasks = prepareSwappedPrompts("It's a force.", "Matter attracts matter.", 42L);
        System.out.println("Eval Tasks: " + evalTasks);
        
        List<Boolean> judge = Arrays.asList(true, false, true, true, false); // [Pass, Fail, Pass, Pass, Fail]
        List<Boolean> human = Arrays.asList(true, true, true, true, false);  // [Pass, Pass, Pass, Pass, Fail]
        
        double agreement = calculateAgreementScore(judge, human);
        System.out.println("Judge/Human Agreement (Expected 0.8): " + agreement);
        
        evaluateQualityGate(0.50, 0.65, false); // Fails due to uncertainty
    }
}
```

**Python Implementation:**
```python
import hashlib
import random
from enum import Enum
from typing import List

class EvaluationSplit(Enum):
    TRAIN = 1
    VALIDATION = 2
    TEST = 3

class DatasetItem:
    def __init__(self, tenant_id: str, prompt: str, expected_answer: str, split: EvaluationSplit):
        self.tenant_id = tenant_id
        self.prompt = prompt
        self.expected_answer = expected_answer
        self.split = split

# Quality Gates Constants
MAX_COST_USD = 1.00
UNCERTAINTY_THRESHOLD = 0.7

# 1. Tenant Privacy and Leakage Control via Hashing
def hash_for_privacy(tenant_id: str, text: str) -> str:
    combined = f"{tenant_id}:{text}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

# 2. Position Swaps & Random Seed Controls (Mitigate specific biases but do not prove correctness)
def prepare_swapped_prompts(model_a: str, model_b: str, seed: int) -> List[str]:
    random.seed(seed)
    prompts = [
        f"Compare Model A: {model_a} vs Model B: {model_b}",
        f"Compare Model A: {model_b} vs Model B: {model_a}"
    ]
    if random.choice([True, False]):
        prompts.reverse()
    return prompts

# 3. Judge/Human Disagreement Worked Score Example
def calculate_agreement_score(judge_pass_fail: List[bool], human_pass_fail: List[bool]) -> float:
    judge_size = len(judge_pass_fail)
    human_size = len(human_pass_fail)
    if judge_size != human_size or not judge_pass_fail:
        return 0.0
    matches = sum(1 for j, h in zip(judge_pass_fail, human_pass_fail) if j == h)
    return matches / judge_size

# 4. Quality Gates
def evaluate_quality_gate(cost_usd: float, confidence_score: float, did_abstain: bool) -> bool:
    if cost_usd > MAX_COST_USD:
        print("Blocked: Evaluation cost exceeded budget.")
        return False
    if did_abstain:
        print("Blocked: Judge model abstained from evaluation. Escalating to human.")
        return False
    if confidence_score < UNCERTAINTY_THRESHOLD:
        print("Blocked: High uncertainty detected. Escalating to human.")
        return False
    
    print("Gate Passed.")
    return True

if __name__ == "__main__":
    item = DatasetItem("tenant_99", "Explain gravity.", "A force of attraction...", EvaluationSplit.TEST)
    print(f"Private Hash: {hash_for_privacy(item.tenant_id, item.prompt)}")
    
    eval_tasks = prepare_swapped_prompts("It's a force.", "Matter attracts matter.", 42)
    print(f"Eval Tasks: {eval_tasks}")
    
    judge = [True, False, True, True, False] # [Pass, Fail, Pass, Pass, Fail]
    human = [True, True, True, True, False]  # [Pass, Pass, Pass, Pass, Fail]
    
    agreement = calculate_agreement_score(judge, human)
    print(f"Judge/Human Agreement (Expected 0.8): {agreement}")
    
    evaluate_quality_gate(0.50, 0.65, False) # Fails due to uncertainty
```
