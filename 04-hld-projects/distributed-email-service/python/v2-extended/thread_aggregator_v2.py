"""v2-extended thread aggregator.

Improvement over v1-basic (named per the repo rule v1-basic -> v2-extended):
3. Order-independent conversation threading (PITFALLS #5, brittle
   threading): v1 grouped a reply into its parent's thread only if the
   parent appeared EARLIER in the input list, so a reply delivered before
   its parent (normal for external mail) started a phantom thread. v2
   indexes messages by Message-ID first, then walks each message's
   In-Reply-To / References chain up to the thread root regardless of
   arrival order, with a cycle guard for malformed headers, and returns
   each thread sorted by timestamp.
"""

from typing import List, Dict


class ThreadAggregator:
    @staticmethod
    def group_messages_into_threads(messages: List[any]) -> List[List[any]]:
        by_id: Dict[str, any] = {msg.message_id: msg for msg in messages}

        def find_root(msg) -> str:
            seen = set()
            current = msg
            while current.message_id not in seen:
                seen.add(current.message_id)
                parent = None
                if current.in_reply_to and current.in_reply_to in by_id:
                    parent = by_id[current.in_reply_to]
                elif current.references:
                    for ref in current.references:
                        if ref in by_id:
                            parent = by_id[ref]
                            break
                if parent is None:
                    return current.message_id
                current = parent
            # Cycle in the headers: anchor the whole cycle at one shared,
            # deterministic id so every member lands in the same thread.
            return min(seen)

        thread_map: Dict[str, List[any]] = {}
        for msg in messages:
            root_id = find_root(msg)
            if root_id not in thread_map:
                thread_map[root_id] = []
            thread_map[root_id].append(msg)

        for thread in thread_map.values():
            thread.sort(key=lambda m: m.timestamp)

        return list(thread_map.values())
