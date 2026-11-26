<!-- Register in concepts README. -->
# Interview Questions and Answers: Fine-Tuning and Adaptation

## 1. What is the fundamental difference between RAG and Fine-Tuning?
RAG (Retrieval-Augmented Generation) provides external knowledge to the model at inference time by injecting it into the prompt. Fine-tuning modifies the model's internal weights to internalize patterns, behaviors, or domain-specific styles. RAG is better for factual, dynamic knowledge, while fine-tuning is better for teaching the model a specific format, tone, or complex task.

## 2. When would you explicitly choose NOT to fine-tune an LLM?
You should avoid fine-tuning when the domain knowledge changes frequently (e.g., daily news), when you lack high-quality training data, or when the task can be solved adequately using few-shot prompting on a base model, as fine-tuning introduces significant infrastructure complexity.

## 3. Explain the memory requirements for full Supervised Fine-Tuning (SFT) of a 7B parameter model using AdamW in fp16.
A 7B model requires roughly 14GB for fp16 weights. However, training requires storing gradients (14GB) and AdamW optimizer states (fp32 momentum and variance = 8 bytes/param = 56GB). Additionally, memory is needed for activations. Thus, the static memory footprint exceeds 84GB, making it impossible to fit on a single 80GB GPU without techniques like ZeRO offloading.

## 4. How does LoRA (Low-Rank Adaptation) solve the memory bottleneck of SFT?
LoRA freezes the pre-trained model weights and injects trainable rank decomposition matrices (A and B) into the transformer layers. By doing so, the number of trainable parameters is reduced by 99% or more. Optimizer states and gradients are only tracked for these tiny matrices, dropping the memory requirement from >84GB to around 16GB for a 7B model.

## 5. What is QLoRA, and how does it differ from standard LoRA?
QLoRA quantizes the frozen base model weights down to 4-bit NormalFloat (NF4) precision, further reducing the memory footprint of the base model. The LoRA adapters remain in higher precision (e.g., bf16). This allows fine-tuning large models (like 7B or 13B) on consumer-grade GPUs with 24GB of VRAM or less.

## 6. What is Catastrophic Forgetting in the context of LLM fine-tuning, and how can it be mitigated?
Catastrophic forgetting occurs when a model loses its general capabilities or prior knowledge while learning new domain-specific tasks. It can be mitigated by using Parameter-Efficient Fine-Tuning (PEFT) like LoRA (which isolates changes), lowering the learning rate, or mixing general-purpose instruction data with the domain-specific data during training (replay).

## 7. Briefly describe the three stages of RLHF (Reinforcement Learning from Human Feedback).
1. **SFT:** Train the base model on high-quality demonstration data.
2. **Reward Model:** Train a separate model on comparison data to predict human preferences.
3. **PPO (Proximal Policy Optimization):** Use reinforcement learning to optimize the SFT model to maximize the reward model's score, while applying a KL divergence penalty to prevent it from deviating too much from the original SFT model.

## 8. Why is DPO (Direct Preference Optimization) becoming more popular than PPO-based RLHF?
DPO is mathematically simpler and much more computationally stable. It eliminates the need to train a separate Reward Model and avoids the unstable, memory-intensive PPO algorithm. Instead, it directly optimizes the policy using a simple cross-entropy objective on chosen and rejected response pairs.

## 9. What is Knowledge Distillation in the context of LLMs?
Knowledge Distillation involves training a smaller "student" model to mimic the outputs, probabilities, or reasoning traces of a larger "teacher" model (like GPT-4). This allows developers to achieve high performance on specific tasks using a much smaller, cheaper model in production.

## 10. How does Adapter Serving enable massive multi-tenancy in LLM deployments?
With techniques like LoRA, the fine-tuned adapters are very small (e.g., 50MB) compared to the base model (e.g., 14GB). In a serving system like vLLM, the large base model is loaded onto the GPU once. For a batched request, the system dynamically loads the specific adapter weights for different users on the fly, allowing a single GPU to serve hundreds of custom models simultaneously.

## 11. What role does "Data Curation" play in the success of SFT?
Data curation is critical; "less is more" for alignment. A small dataset (e.g., 1,000 examples) of extremely high-quality, diverse, and perfectly formatted data will yield much better fine-tuning results than 100,000 noisy or poorly formatted examples. De-duplication and filtering are essential steps.

## 12. If a fine-tuned model starts hallucinating facts it used to know, what likely went wrong?
The model likely suffered from catastrophic forgetting due to over-optimization on the new dataset, using a learning rate that was too high, training for too many epochs, or not including a mix of general instruction data in the training set.

## 13. Can RAG and Fine-Tuning be used together? Give an example.
Yes. You can fine-tune a model to consistently output responses in a very specific, complex JSON schema. Then, at inference time, you use RAG to fetch real-time data and inject it into the prompt. The fine-tuning ensures the structure is correct, while RAG ensures the content is factually up-to-date.

## 14. What are the economic trade-offs between long-context prompting and fine-tuning?
Long-context prompting requires zero upfront training cost but incurs high latency and high cost per inference request due to the large token volume. Fine-tuning has an upfront compute cost to train the model but allows for much shorter prompts at inference, leading to lower latency and lower per-request costs, making it cost-effective at scale.

## 15. In QLoRA, what is the purpose of the "Paged Optimizer"?
The paged optimizer manages memory spikes during training. If the GPU runs out of VRAM (e.g., during gradient computation for large batches), the paged optimizer seamlessly evicts optimizer states to the CPU RAM and pages them back into GPU memory when needed, preventing Out-Of-Memory (OOM) errors.
