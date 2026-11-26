from typing import List, Callable, Dict, Optional
import threading

class ZNode:
    def __init__(self, name: str, data: str, ephemeral: bool = False, session_id: Optional[str] = None):
        self.name = name
        self.data = data
        self.ephemeral = ephemeral
        self.session_id = session_id

class ZkSimulator:
    def __init__(self):
        self.nodes: Dict[str, ZNode] = {}
        self.watches: Dict[str, List[Callable]] = {}
        self.sequence_number = 0
        self.lock = threading.Lock()

    def create(self, path: str, data: str, ephemeral: bool = False, sequential: bool = False, session_id: Optional[str] = None) -> str:
        with self.lock:
            final_path = path
            if sequential:
                final_path = f"{path}{self.sequence_number:010d}"
                self.sequence_number += 1

            if final_path in self.nodes:
                raise ValueError("Node already exists")

            self.nodes[final_path] = ZNode(final_path, data, ephemeral, session_id)
            return final_path

    def get_children(self, parent_path: str) -> List[str]:
        with self.lock:
            # Simple prefix match for children simulation.
            # E.g., if parent_path is "/election", children are "/election/node_001" etc.
            # We return just the child node name, not full path, for simplicity or full path based on need.
            # Let's return just the suffix to match real ZK getChildren, or full path.
            # Real ZK returns node names relative to parent.
            prefix = parent_path if parent_path.endswith('/') else f"{parent_path}/"
            children = []
            for path in self.nodes:
                if path.startswith(prefix):
                    suffix = path[len(prefix):]
                    if '/' not in suffix:
                        children.append(suffix)
            return children

    def exists(self, path: str, watch: Optional[Callable] = None) -> bool:
        with self.lock:
            exists = path in self.nodes
            if watch:
                if path not in self.watches:
                    self.watches[path] = []
                self.watches[path].append(watch)
            return exists

    def delete(self, path: str):
        with self.lock:
            if path in self.nodes:
                del self.nodes[path]
                self._trigger_watches(path)

    def _trigger_watches(self, path: str):
        if path in self.watches:
            callbacks = self.watches[path]
            self.watches[path] = [] # Watches are one-shot
            for cb in callbacks:
                cb(path)

    def expire_session(self, session_id: str):
        with self.lock:
            paths_to_delete = []
            for path, node in self.nodes.items():
                if node.ephemeral and node.session_id == session_id:
                    paths_to_delete.append(path)

            for path in paths_to_delete:
                del self.nodes[path]

            # Trigger watches without lock to avoid deadlocks in callbacks

        for path in paths_to_delete:
            self._trigger_watches(path)

class ZkLeaderElector:
    def __init__(self, zk: ZkSimulator, election_path: str, session_id: str):
        self.zk = zk
        self.election_path = election_path
        self.session_id = session_id
        self.node_path = None
        self.is_leader = False
        self.on_leadership_change = None

        # Ensure election path exists
        if not self.zk.exists(self.election_path):
            try:
                self.zk.create(self.election_path, "election_parent")
            except ValueError:
                pass # Already created by another

    def join_election(self):
        # Create ephemeral sequential node
        prefix = f"{self.election_path}/n_"
        self.node_path = self.zk.create(prefix, self.session_id, ephemeral=True, sequential=True, session_id=self.session_id)
        self.check_leadership()

    def check_leadership(self):
        children = self.zk.get_children(self.election_path)
        # Sort children by sequence number
        children.sort()

        # Get my node name (strip election path prefix)
        my_node_name = self.node_path.split('/')[-1]

        if not children:
            return

        if my_node_name == children[0]:
            self.is_leader = True
            if self.on_leadership_change:
                self.on_leadership_change(True)
        else:
            self.is_leader = False
            if self.on_leadership_change:
                self.on_leadership_change(False)

            # Watch the node immediately preceding me
            my_index = children.index(my_node_name)
            preceding_node_name = children[my_index - 1]
            preceding_path = f"{self.election_path}/{preceding_node_name}"

            # Check if preceding node exists and set watch
            if not self.zk.exists(preceding_path, watch=self._on_preceding_node_deleted):
                # If it doesn't exist, we must check leadership again
                self.check_leadership()

    def _on_preceding_node_deleted(self, path):
        # Called when preceding node is deleted (e.g., session expiration)
        self.check_leadership()
