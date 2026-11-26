import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-append')))

from append_store import AppendStore

def test_append_and_range_query():
    store = AppendStore()
    store.append(100, 1.0)
    store.append(200, 2.0)
    store.append(300, 3.0)
    store.append(400, 4.0)
    
    res = store.range_query(150, 350)
    assert len(res) == 2
    assert res[0] == (200, 2.0)
    assert res[1] == (300, 3.0)
    
    with pytest.raises(ValueError):
        store.append(250, 5.0)

