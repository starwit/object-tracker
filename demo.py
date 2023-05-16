import os
import json
from objecttracker.config import ObjectTrackerConfig, DeepOcSortConfig
from objecttracker.tracker import Tracker
from visionapi.detector_pb2 import DetectionOutput
from visionapi.tracker_pb2 import TrackingOutput
from google.protobuf.text_format import Parse
from google.protobuf.json_format import MessageToDict


def detection_iter(path):
    files = sorted(os.listdir(path))
    for file in files:
        basename = os.path.splitext(file)[0]
        with open(os.path.join(path, file), 'r') as f:
            content = f.read()
        detection = Parse(content, DetectionOutput()).SerializeToString()
        yield basename, detection

def deserialize_proto(message):
    track_output = TrackingOutput()
    track_output.ParseFromString(message)
    return track_output

TRACKING_CONFIG = ObjectTrackerConfig(
    tracking_params=DeepOcSortConfig(
        det_thresh=0.25,
        model_weights='osnet_x0_25_msmt17.pt',
    ),
    device='cpu',
)

tracker = Tracker(TRACKING_CONFIG)

tracker.start()

for basename, detection in detection_iter('.demo_detections'):
    tracker.put_detection(detection)
    track_message = tracker.get_tracking(timeout=None)
    track_proto = deserialize_proto(track_message)
    tracked_detections = MessageToDict(track_proto)['trackedDetections']
    print(f'{basename}: {json.dumps(tracked_detections)}')

tracker.stop()