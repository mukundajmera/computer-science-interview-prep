# Accounts Merge

## Overview

Given accounts with names and email addresses, merge accounts that share at least one email.

Union-Find groups emails or account indexes into connected components. The important interview step is choosing stable ids and reconstructing sorted output.

## Requirements and constraints

- Accounts sharing any email belong to the same person.
- Names may be repeated across different people.
- Output emails are usually sorted within each merged account.
- Clarify whether conflicting names can appear in one connected component.
- Input size can be large, so avoid pairwise account comparison.

## Recognition cue

"Merge records that share an identifier" is an identity-component problem.

## Invariant or state definition

Every email maps to one DSU id. Emails in the same connected component belong to one merged account.

## High-level design / approach

1. Map each new email to an id.
2. For each account, union the first email with every other email in that account.
3. Record an email-to-name mapping or account-owner rule.
4. After all unions, group emails by `find(email_id)`.
5. Sort each group's emails and prepend the chosen name.

## Dry run

Accounts:

```text
John: a@mail, b@mail
John: b@mail, c@mail
Mary: z@mail
```

Unioning through `b@mail` creates one component `{a@mail, b@mail, c@mail}` for John. Mary remains separate.

## Language-neutral pseudocode

```text
for account in accounts:
    name = account[0]
    emails = account[1:]
    for email in emails:
        id = get_or_create_id(email)
        email_to_name[email] = name
    for email in emails[1:]:
        dsu.union(id_of(emails[0]), id_of(email))

groups = map root -> list emails
for email, id in email_to_id:
    groups[dsu.find(id)].append(email)

return [name_for_group(root)] + sorted(emails) for each group
```

## Complexity proof

Let `E` be total email occurrences and `U` unique emails. DSU operations cost `O(E * alpha(U))`. Sorting grouped emails costs up to `O(U log U)` across all groups. Space is `O(U)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Id mapping | Maps email strings to stable DSU ids |
| Merge rule | Unions emails within the same account |
| Grouping | Groups by final root after all unions |
| Output | Sorts emails and handles names explicitly |
| Complexity | Avoids pairwise account comparison |

## Common pitfalls

1. Merging by name instead of shared email.
2. Comparing every pair of accounts.
3. Grouping by stale parent without calling `find`.
4. Forgetting to sort emails.
5. Losing isolated single-email accounts.

## Follow-up questions

1. What if names conflict inside a component?
2. How would you stream account merges over time?
3. How would you audit why two accounts merged?
4. How would privacy rules affect this design?

## Variants and extensions

- Identity graph clustering.
- Contact deduplication.
- Device or cookie merge.
- Fraud cluster construction.

## Cross-links

- [Union-Find Overview](./01-overview.md)
- [Bot Detection Platform](../../04-hld-projects/bot-detection-platform/)
- [Distributed Coordination](../../03-hld-concepts/distributed-coordination/THEORY.md)
