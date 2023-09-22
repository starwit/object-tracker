import logging
import time
import uuid
from pathlib import Path
from typing import Any

import numpy as np
import torch
from prometheus_client import Counter, Histogram, Summary
from visionapi.messages_pb2 import DetectionOutput, TrackingOutput

from .config import ObjectTrackerConfig
from .trackingimpl.deepocsort.ocsort import OCSort

logging.basicConfig(format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)

GET_DURATION = Histogram('object_tracker_get_duration', 'The time it takes to deserialize the proto until returning the detection result as a serialized proto',
                         buckets=(0.0025, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25))
MODEL_DURATION = Summary('object_tracker_tracker_update_duration', 'How long the tracker update takes')
OBJECT_COUNTER = Counter('object_tracker_object_counter', 'How many objects have been tracked')


class Tracker:
    def __init__(self, config: ObjectTrackerConfig) -> None:
        self.config = config
        logger.setLevel(self.config.log_level.value)

        self.object_id_seed = uuid.uuid4()
        self._setup()
        
    def __call__(self, input_proto, *args, **kwargs) -> Any:
        return self.get(input_proto)

    @GET_DURATION.time()
    @torch.no_grad()
    def get(self, input_proto):        

        input_image, detection_proto = self._unpack_proto(input_proto)
        
        inference_start = time.monotonic_ns()
        det_array = self._prepare_detection_input(detection_proto)
        tracking_output_array = self.tracker.update(det_array, input_image)

        OBJECT_COUNTER.inc(len(tracking_output_array))
        
        inference_time_us = (time.monotonic_ns() - inference_start) // 1000
        return self._create_output(tracking_output_array, detection_proto, inference_time_us)
        
    def _setup(self):
        logger.info('Setting up object-tracker model...')
        self.tracker = OCSort(
            Path(self.config.tracking_params.model_weights), 
            torch.device(self.config.device), 
            self.config.tracking_params.fp16, 
            self.config.tracking_params.det_thresh,
        )

    def _unpack_proto(self, detection_proto_raw):
        detection_proto = DetectionOutput()
        detection_proto.ParseFromString(detection_proto_raw)

        input_frame = detection_proto.frame
        input_image = np.frombuffer(input_frame.frame_data, dtype=np.uint8) \
            .reshape((input_frame.shape.height, input_frame.shape.width, input_frame.shape.channels))

        return input_image, detection_proto
    
    def _prepare_detection_input(self, detection_proto: DetectionOutput):
        det_array = np.zeros((len(detection_proto.detections), 6))
        for idx, detection in enumerate(detection_proto.detections):
            det_array[idx, 0] = detection.bounding_box.min_x
            det_array[idx, 1] = detection.bounding_box.min_y
            det_array[idx, 2] = detection.bounding_box.max_x
            det_array[idx, 3] = detection.bounding_box.max_y

            det_array[idx, 4] = detection.confidence
            det_array[idx, 5] = detection.class_id
        return det_array
    
    def _create_output(self, tracking_output, detection_proto: DetectionOutput, inference_time_us):
        output_proto = TrackingOutput()
        output_proto.frame.CopyFrom(detection_proto.frame)

        # The length of detections and tracking_output can be different 
        # (as the latter only includes objects that could be matched to an id)
        # Therefore, we can only reuse the VideoFrame and have to recreate everything else
        
        for pred in tracking_output:
            tracked_detection = output_proto.tracked_detections.add()
            tracked_detection.detection.bounding_box.min_x = int(pred[0])
            tracked_detection.detection.bounding_box.min_y = int(pred[1])
            tracked_detection.detection.bounding_box.max_x = int(pred[2])
            tracked_detection.detection.bounding_box.max_y = int(pred[3])

            tracked_detection.object_id = uuid.uuid3(self.object_id_seed, str(int(pred[4]))).bytes

            tracked_detection.detection.class_id = int(pred[5])
            tracked_detection.detection.confidence = float(pred[6])

        output_proto.metrics.CopyFrom(detection_proto.metrics)
        output_proto.metrics.tracking_inference_time_us = inference_time_us
        
        return output_proto.SerializeToString()
