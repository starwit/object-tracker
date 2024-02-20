import logging
import time
import uuid
from pathlib import Path
from typing import Any

import numpy as np
import torch
from boxmot import OCSORT, DeepOCSORT
from prometheus_client import Counter, Histogram, Summary
from visionapi.messages_pb2 import DetectionOutput, TrackingOutput
from visionlib.pipeline.tools import get_raw_frame_data

from .config import ObjectTrackerConfig, TrackingAlgorithm

logging.basicConfig(format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)

GET_DURATION = Histogram('object_tracker_get_duration', 'The time it takes to deserialize the proto until returning the detection result as a serialized proto',
                         buckets=(0.0025, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25))
MODEL_DURATION = Summary('object_tracker_tracker_update_duration', 'How long the tracker update takes')
OBJECT_COUNTER = Counter('object_tracker_object_counter', 'How many objects have been tracked')
PROTO_SERIALIZATION_DURATION = Summary('object_tracker_proto_serialization_duration', 'The time it takes to create a serialized output proto')
PROTO_DESERIALIZATION_DURATION = Summary('object_tracker_proto_deserialization_duration', 'The time it takes to deserialize an input proto')


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
        with MODEL_DURATION.time():
            tracking_output_array = self.tracker.update(det_array, input_image)

        OBJECT_COUNTER.inc(len(tracking_output_array))
        
        inference_time_us = (time.monotonic_ns() - inference_start) // 1000
        return self._create_output(tracking_output_array, detection_proto, inference_time_us)
        
    def _setup(self):
        conf = self.config.tracker_config
        if self.config.tracker_algorithm == TrackingAlgorithm.DEEPOCSORT:
            self.tracker = DeepOCSORT(
                model_weights=Path(self.config.tracker_config.model_weights),
                device=conf.device,
                fp16=conf.fp16,
                per_class=conf.per_class,
                det_thresh=conf.det_thresh,
                max_age=conf.max_age,
                min_hits=conf.min_hits,
                iou_threshold=conf.iou_threshold,
                delta_t=conf.delta_t,
                asso_func=conf.asso_func,
                inertia=conf.inertia,
                w_association_emb=conf.w_association_emb,
                alpha_fixed_emb=conf.alpha_fixed_emb,
                aw_param=conf.aw_param,
                embedding_off=conf.embedding_off,
                cmc_off=conf.cmc_off,
                aw_off=conf.aw_off,
                new_kf_off=conf.new_kf_off
            )
        elif self.config.tracker_algorithm == TrackingAlgorithm.OCSORT:
            self.tracker = OCSORT(
                det_thresh=conf.det_thresh,
                max_age=conf.max_age,
                min_hits=conf.min_hits,
                asso_threshold=conf.asso_threshold,
                delta_t=conf.delta_t,
                asso_func=conf.asso_func,
                inertia=conf.inertia,
                use_byte=conf.use_byte
            )
        else:
            logger.error(f'Unknown tracker algorithm: {self.config.tracker_algorithm}')
            exit(1)

    @PROTO_DESERIALIZATION_DURATION.time()
    def _unpack_proto(self, detection_proto_raw):
        detection_proto = DetectionOutput()
        detection_proto.ParseFromString(detection_proto_raw)

        input_frame = detection_proto.frame
        input_image = get_raw_frame_data(input_frame)

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
    
    @PROTO_SERIALIZATION_DURATION.time()
    def _create_output(self, tracking_output, detection_proto: DetectionOutput, inference_time_us):
        output_proto = TrackingOutput()
        output_proto.frame.CopyFrom(detection_proto.frame)

        # The length of detections and tracking_output can be different 
        # (as the latter only includes objects that could be matched to an id)
        # Therefore, we can only reuse the VideoFrame and have to recreate everything else
        
        for pred in tracking_output:
            tracked_detection = output_proto.tracked_detections.add()
            tracked_detection.detection.bounding_box.min_x = float(pred[0])
            tracked_detection.detection.bounding_box.min_y = float(pred[1])
            tracked_detection.detection.bounding_box.max_x = float(pred[2])
            tracked_detection.detection.bounding_box.max_y = float(pred[3])

            tracked_detection.object_id = uuid.uuid3(self.object_id_seed, str(int(pred[4]))).bytes

            tracked_detection.detection.confidence = float(pred[5])
            tracked_detection.detection.class_id = int(pred[6])

        output_proto.metrics.CopyFrom(detection_proto.metrics)
        output_proto.metrics.tracking_inference_time_us = inference_time_us
        
        return output_proto.SerializeToString()
