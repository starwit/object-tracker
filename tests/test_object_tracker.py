import pytest

def test_tracker_import():
    try:
        from objecttracker.tracker import Tracker
    except ImportError as e:
        pytest.fail(f"Failed to import ObjectTracker: {e}")

    assert ObjectTracker is not None, "ObjectTracker should be imported successfully"
        
        