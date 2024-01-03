import argparse
import signal
import threading
import os

import cv2
import redis
from visionapi.messages_pb2 import (Detection, DetectionOutput,
                                    TrackedDetection, TrackingOutput,
                                    VideoFrame)
from visionlib.pipeline.consumer import RedisConsumer
from visionlib.pipeline.tools import get_raw_frame_data

ANNOTATION_COLOR = (0, 0, 255)


# Function to annotate images
def annotate(image, detection: Detection, object_id: bytes = None):
    bbox_x1 = detection.bounding_box.min_x
    bbox_y1 = detection.bounding_box.min_y
    bbox_x2 = detection.bounding_box.max_x
    bbox_y2 = detection.bounding_box.max_y

    class_id = detection.class_id
    conf = detection.confidence

    label = f'{class_id} - {round(conf,2)}'

    if object_id is not None:
        object_id = object_id.hex()[:4]
        label = f'ID {object_id} - {class_id} - {round(conf,2)}'

    line_width = max(round(sum(image.shape) / 2 * 0.002), 2)

    cv2.rectangle(image, (bbox_x1, bbox_y1), (bbox_x2, bbox_y2), color=ANNOTATION_COLOR, thickness=line_width, lineType=cv2.LINE_AA)
    cv2.putText(image, label, (bbox_x1, bbox_y1 - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=ANNOTATION_COLOR, thickness=round(line_width/3), fontScale=line_width/4, lineType=cv2.LINE_AA)


def saveImage(image, path, i):
    if not os.path.exists(path):
        os.makedirs(path)
    filename = f"frame_{i}.jpg"
    cv2.imwrite(os.path.join(path, filename), image)
    

def source_output_handler(frame_message, path, i):
    frame_proto = VideoFrame()
    frame_proto.ParseFromString(frame_message)
    image = get_raw_frame_data(frame_proto)

    saveImage(image, path, i)

   

def detection_output_handler(detection_message, path, i):
    detection_proto = DetectionOutput()
    detection_proto.ParseFromString(detection_message)
    image = get_raw_frame_data(detection_proto.frame)

    for detection in detection_proto.detections:
        annotate(image, detection)

    saveImage(image, path, i)
    
def tracking_output_handler(tracking_message, path, i):
    track_proto = TrackingOutput()
    track_proto.ParseFromString(tracking_message)
    image = get_raw_frame_data(track_proto.frame)

    for tracked_det in track_proto.tracked_detections:
        annotate(image, tracked_det.detection, tracked_det.object_id)

    saveImage(image, path, i)

STREAM_TYPE_HANDLER = {
    'videosource': source_output_handler,
    'objectdetector': detection_output_handler,
    'objecttracker': tracking_output_handler,
}



"""
# Main function
if __name__ == '__main__':
    path = 'benchmarks/frames/'
   
    STREAM_KEY = "objecttracker:test_stream"
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    

    consume = RedisConsumer(REDIS_HOST, REDIS_PORT, [STREAM_KEY], block=200)

    i = 0

    with consume:
        for stream_key, proto_data in consume():
           
            if stream_key is None:
                continue
            else:
                i = i + 1
                stream_type, stream_id = stream_key.split(':')
                print(stream_type)
                STREAM_TYPE_HANDLER[stream_type](proto_data, path, i)

"""

def save_as_image(path, proto_data, i):
    STREAM_TYPE_HANDLER["objecttracker"](proto_data, path, i)

