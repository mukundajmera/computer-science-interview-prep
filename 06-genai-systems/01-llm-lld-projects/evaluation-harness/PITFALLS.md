## Common pitfalls
1. Over-reliance on exact string matching for generative outputs, leading to false negatives.
2. Inconsistent normalization (casing, punctuation, whitespace) skewing evaluation scores.
3. Division by zero in precision/recall calculations when predicted or ground-truth token sets are empty.
4. Tightly coupling the evaluation harness to live LLM API calls, making offline benchmarking slow and expensive.
5. Inability to evaluate deterministic vs non-deterministic tasks with appropriate threshold tolerances.

## Why these fail interviews
- Fails to recognize the non-deterministic nature of generative AI outputs.
- Inflexible metric implementations that break on real-world test sets.

## Mitigations
- Implement canonical tokenization and text normalization prior to metric evaluation.
- Provide defensive bounds checks for precision, recall, and F1 calculations.
- Use mockable model outputs and decouple dataset evaluation from live network inference.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
