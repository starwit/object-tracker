import pytest
from objecttracker.tracker import Tracker
from objecttracker.config import ObjectTrackerConfig

@pytest.fixture
def tracker():
    config = ObjectTrackerConfig()  # Initialize with appropriate parameters
    return Tracker(config)

def test_tracker_initialization(tracker):
    assert tracker is not None

#def test_tracker_call(tracker):
    #input_proto = b'...'  # Replace with a valid proto input
    #result = tracker(input_proto)
    #assert result is not None  # Adjust based on expected output

#def test_get_method(tracker):
    #input_proto = b'...'  # Replace with a valid proto input
    #result = tracker.get(input_proto)
    #assert result is not None  # Adjust based on expected output

#def test_unpack_proto(tracker):
    #sae_message_bytes = b'...'  # Replace with valid bytes
    #result = tracker._unpack_proto(sae_message_bytes)
    #assert result is not None  # Adjust based on expected output

#def test_create_output(tracker):
    #tracking_output = {}  # Replace with valid tracking output
    #input_sae_msg = None  # Replace with valid SaeMessage instance
    #inference_time_us = 1000  # Example inference time
    #result = tracker._create_output(tracking_output, input_sae_msg, inference_time_us)
    #assert result is not None  # Adjust based on expected output