import json
import os

import cv2
import numpy as np
from google.protobuf.json_format import MessageToDict
from google.protobuf.text_format import Parse
from ultralytics.yolo.utils.plotting import Annotator
from visionapi.messages_pb2 import DetectionOutput, TrackingOutput

from objecttracker.config import DeepOcSortConfig, ObjectTrackerConfig, LogLevel
from objecttracker.tracker import Tracker


def detection_iter(path):
    files = sorted(os.listdir(path))
    for file in files:
        basename = os.path.splitext(file)[0]
        with open(os.path.join(path, file), 'rb') as f:
            content = f.read()
        yield basename, content

def deserialize_proto(message):
    track_output = TrackingOutput()
    track_output.ParseFromString(message)
    return track_output

def create_output_image(track_proto: TrackingOutput):
    img_shape = track_proto.frame.shape
    img_bytes = track_proto.frame.frame_data
    img = np.frombuffer(img_bytes, dtype=np.uint8).reshape((img_shape.height, img_shape.width, img_shape.channels))

    return annotate(img, track_proto)

def annotate(image, track_proto: TrackingOutput):
    ann = Annotator(image)
    for detection in track_proto.tracked_detections:
        bbox_x1 = detection.detection.bounding_box.min_x
        bbox_y1 = detection.detection.bounding_box.min_y
        bbox_x2 = detection.detection.bounding_box.max_x
        bbox_y2 = detection.detection.bounding_box.max_y

        class_id = detection.detection.class_id
        conf = detection.detection.confidence
        object_id = int.from_bytes(detection.object_id, 'big')

        ann.box_label((bbox_x1, bbox_y1, bbox_x2, bbox_y2), f'ID {object_id} - {class_id} - {round(conf,2)}')

    return ann.result()
    

TRACKING_CONFIG = ObjectTrackerConfig(
    log_level=LogLevel.INFO,
    tracking_params=DeepOcSortConfig(
        det_thresh=0.25,
        model_weights='osnet_x0_25_msmt17.pt',
    ),
    device='cuda:0',
)

tracker = Tracker(TRACKING_CONFIG)

for basename, detection in detection_iter('.demo_detections'):
    track_message = tracker.get(detection)
    track_proto = deserialize_proto(track_message)
    print(f'Inference time: {track_proto.metrics.tracking_inference_time_us} us')
    tracked_detections = MessageToDict(track_proto)['trackedDetections']
    cv2.imshow('window', create_output_image(track_proto))
    cv2.waitKey(1)
    # print(f'{basename}: {json.dumps(tracked_detections)}')

cv2.destroyAllWindows()
