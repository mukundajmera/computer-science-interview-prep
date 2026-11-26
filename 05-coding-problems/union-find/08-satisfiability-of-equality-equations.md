# Satisfiability of Equality Equations

## Overview

Given equations like `a==b` and `a!=b`, determine whether all constraints can be satisfied.

Union-Find works because equality forms equivalence classes. Inequality is valid only if its two variables end in different classes.

## Requirements and constraints

- Variables are usually lowercase letters, but confirm the domain.
- Equality is transitive: if `a==b` and `b==c`, then `a==c`.
- Inequality is a contradiction when both sides have the same root.
- Process all equalities before checking inequalities.
- Self-inequality such as `a!=a` is impossible.

## Recognition cue

"Equality constraints" plus "possible/impossible" means build equivalence classes first, then test contradictions.

## Invariant or state definition

After processing all equality equations, `find(x)` identifies the equivalence class for variable `x`. Every inequality must compare two different roots.

## High-level design / approach

1. Initialize DSU for all variables.
2. First pass: union variables from every `==` equation.
3. Second pass: for every `!=` equation, check roots.
4. If any inequality has equal roots, return false.
5. Otherwise return true.

## Dry run

Equations: `a==b`, `b==c`, `a!=c`.

After equalities, `a`, `b`, and `c` share one root. The inequality `a!=c` compares the same root, so the set is unsatisfiable.

## Language-neutral pseudocode

```text
possible(equations):
    dsu = DSU(all variables)
    for eq in equations:
        if eq.operator == "==":
            dsu.union(eq.left, eq.right)

    for eq in equations:
        if eq.operator == "!=":
            if dsu.find(eq.left) == dsu.find(eq.right):
                return false
    return true
```

## Complexity proof

For `e` equations and `v` variables, processing costs `O(e * alpha(v))`. Space is `O(v)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Order | Processes all equalities before inequalities |
| Contradiction | Detects same-root inequality |
| Transitivity | Uses DSU to capture equivalence classes |
| Edge cases | Handles `a!=a` and duplicate equations |
| Complexity | Uses variables and equation count |

## Common pitfalls

1. Checking inequalities before all equalities are known.
2. Comparing only direct pairs and missing transitive equality.
3. Forgetting self-inequality.
4. Overcomplicating with graph traversal for fixed small domains.
5. Not mapping variables when the domain is larger than lowercase letters.

## Follow-up questions

1. How would you explain the two-pass order?
2. How would you support more than 26 variables?
3. What if equations arrive online and queries ask after each one?
4. What if constraints include less-than or greater-than?

## Variants and extensions

- Constraint consistency checks.
- Alias and identity equivalence.
- Type unification basics.
- Offline policy contradiction detection.

## Cross-links

- [Union-Find Overview](./01-overview.md)
- [Accounts Merge](./05-accounts-merge.md)
- [Distributed Coordination](../../03-hld-concepts/distributed-coordination/THEORY.md)
