import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from visionapi.messages_pb2 import DetectionOutput, TrackingOutput

from .config import ObjectTrackerConfig
from .trackingimpl.deepocsort.ocsort import OCSort


class Tracker:
    def __init__(self, config: ObjectTrackerConfig) -> None:
        self.config = config

        self._setup()
        
    def __call__(self, input_proto, *args, **kwargs) -> Any:
        return self.get(input_proto)

    @torch.no_grad()
    def get(self, input_proto):        

        input_image, detection_proto = self._unpack_proto(input_proto)
        
        inference_start = time.monotonic_ns()
        det_array = self._prepare_detection_input(detection_proto)
        tracking_output_array = self.tracker.update(det_array, input_image)
        
        inference_time_us = (time.monotonic_ns() - inference_start) // 1000
        return self._create_output(tracking_output_array, detection_proto, inference_time_us)
        
    def _setup(self):
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

            tracked_detection.object_id = int(pred[4]).to_bytes(4, 'big')

            tracked_detection.detection.class_id = int(pred[5])
            tracked_detection.detection.confidence = float(pred[6])

        output_proto.metrics.CopyFrom(detection_proto.metrics)
        output_proto.metrics.tracking_inference_time_us = inference_time_us
        
        return output_proto.SerializeToString()
