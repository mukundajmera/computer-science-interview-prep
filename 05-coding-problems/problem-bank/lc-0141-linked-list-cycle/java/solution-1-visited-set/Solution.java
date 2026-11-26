import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.Set;

class Solution {
    public boolean hasCycle(ListNode head) {
        Set<ListNode> seen = Collections.newSetFromMap(new IdentityHashMap<>());
        ListNode current = head;
        while (current != null) {
            if (!seen.add(current)) {
                return true;
            }
            current = current.next;
        }
        return false;
    }
}
