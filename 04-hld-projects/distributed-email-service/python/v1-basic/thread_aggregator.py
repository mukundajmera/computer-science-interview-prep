from typing import List, Dict
import sys
import os

# dynamic import to avoid relative imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Wait, this might cause circular import. Let's handle typing differently.

class ThreadAggregator:
    @staticmethod
    def group_messages_into_threads(messages: List[any]) -> List[List[any]]:
        thread_map: Dict[str, List[any]] = {}
        message_to_thread_map: Dict[str, str] = {}

        for msg in messages:
            message_id = msg.message_id
            in_reply_to = msg.in_reply_to

            thread_id = None
            if in_reply_to and in_reply_to in message_to_thread_map:
                thread_id = message_to_thread_map[in_reply_to]
            elif msg.references:
                for ref in msg.references:
                    if ref in message_to_thread_map:
                        thread_id = message_to_thread_map[ref]
                        break

            if not thread_id:
                thread_id = message_id

            message_to_thread_map[message_id] = thread_id
            if thread_id not in thread_map:
                thread_map[thread_id] = []
            thread_map[thread_id].append(msg)

        return list(thread_map.values())
