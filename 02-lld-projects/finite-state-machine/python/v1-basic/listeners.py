from typing import Callable

# Listener signature: from_state, to_state, event
StateChangeListener = Callable[[str, str, str], None]
