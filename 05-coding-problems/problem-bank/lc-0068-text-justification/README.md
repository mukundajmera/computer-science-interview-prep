# Text Justification

## Clean-Room Summary

Arrange words into lines of a fixed width, distributing spaces between words for full justification except on the final line.

## Driver Signature

```java
class Solution {
    public List<String> fullJustify(String[] words, int maxWidth) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def fullJustify(self, words: List[str], maxWidth: int) -> List[str]:
        # implementation
```

## Repo-Authored Examples

| words | width | lines |
| --- | ---: | --- |
| `["Fit", "words", "well"]` | `10` | `["Fit  words", "well      "]` |
| `["Short", "line"]` | `8` | `["Short   ", "line    "]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Greedy line builder | `O(total characters)`. | `O(total characters)`. |

## Pitfalls

- The last line is left-justified even when it has multiple words.
- Extra spaces go to earlier gaps when the spacing is uneven.
- A one-word non-final line is padded on the right.
