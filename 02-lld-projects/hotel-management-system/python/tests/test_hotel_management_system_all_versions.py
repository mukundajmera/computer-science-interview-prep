import pytest
import importlib.util
import sys

def load_module(version):
    module_name = f"hotel_management_{version.replace('-', '_')}"
    if version == "v3-optimized":
        file_path = f"02-lld-projects/hotel-management-system/python/{version}/hotel_management_system.py"
    else:
        file_path = f"02-lld-projects/hotel-management-system/python/{version}/hotel.py"
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

VERSIONS = ["v1-basic", "v2-extended", "v3-optimized"]

@pytest.mark.parametrize("version", VERSIONS)
def test_housekeeping_status(version):
    m = load_module(version)
    room = m.Room("101", m.RoomType.STANDARD)
    assert room.status == m.HousekeepingStatus.CLEAN
    
    if hasattr(room, "update_status"):
        room.update_status(m.HousekeepingStatus.INSPECTED)
    else:
        room.mark_inspected()
    assert room.status == m.HousekeepingStatus.INSPECTED

@pytest.mark.parametrize("version", VERSIONS)
def test_check_in(version):
    m = load_module(version)
    manager = m.HotelManager()
    room = m.Room("102", m.RoomType.DELUXE)
    
    if hasattr(room, "update_status"):
        room.update_status(m.HousekeepingStatus.INSPECTED)
    else:
        room.mark_inspected()
        
    manager.add_room(room)
    
    stay = manager.check_in("RES-1", "Alice", m.RoomType.DELUXE)
    assert stay is not None
    assert stay.guest_name == "Alice"
    assert stay.room.room_id == "102"
    assert stay.room.is_occupied == True

@pytest.mark.parametrize("version", VERSIONS)
def test_folio_billing(version):
    m = load_module(version)
    manager = m.HotelManager()
    room = m.Room("103", m.RoomType.SUITE)
    
    if hasattr(room, "update_status"):
        room.update_status(m.HousekeepingStatus.INSPECTED)
    else:
        room.mark_inspected()
        
    manager.add_room(room)
    stay = manager.check_in("RES-2", "Bob", m.RoomType.SUITE)
    
    manager.post_charge("103", "Room Service", 50.0)
    manager.post_charge("103", "Spa", 100.0)
    
    expected_balance_before = 150.0
    assert stay.folio.balance == expected_balance_before
    manager.settle_folio("103", 100.0)
    expected_balance_after = 50.0
    assert stay.folio.balance == expected_balance_after

@pytest.mark.parametrize("version", VERSIONS)
def test_room_keys(version):
    m = load_module(version)
    manager = m.HotelManager()
    room = m.Room("104", m.RoomType.STANDARD)
    
    if hasattr(room, "update_status"):
        room.update_status(m.HousekeepingStatus.INSPECTED)
    else:
        room.mark_inspected()
        
    manager.add_room(room)
    stay = manager.check_in("RES-3", "Charlie", m.RoomType.STANDARD)
    
    key1 = stay.issue_key()
    key2 = stay.issue_key()
    
    assert key1.is_active == True
    assert key2.is_active == True
    assert len(stay.keys) == 2
    
    manager.post_charge("104", "Minibar", 10.0)
    manager.settle_folio("104", 10.0)
    manager.check_out("104")
    
    assert key1.is_active == False
    assert key2.is_active == False

@pytest.mark.parametrize("version", VERSIONS)
def test_check_out_unsettled_folio(version):
    m = load_module(version)
    manager = m.HotelManager()
    room = m.Room("105", m.RoomType.DELUXE)
    
    if hasattr(room, "update_status"):
        room.update_status(m.HousekeepingStatus.INSPECTED)
    else:
        room.mark_inspected()
        
    manager.add_room(room)
    stay = manager.check_in("RES-4", "Dave", m.RoomType.DELUXE)
    
    manager.post_charge("105", "Laundry", 20.0)
    
    with pytest.raises(ValueError, match="Folio must be settled before check-out"):
        manager.check_out("105")
        
    assert stay.room.is_occupied == True
