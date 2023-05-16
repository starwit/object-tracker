import multiprocessing as mp
import queue
import time
from pathlib import Path

import numpy as np
import torch
from visionapi.detector_pb2 import DetectionOutput
from visionapi.tracker_pb2 import TrackingOutput

from .config import ObjectTrackerConfig
from .errors import *
from .trackingimpl.deepocsort.ocsort import OCSort


class Tracker:
    def __init__(self, config: ObjectTrackerConfig) -> None:
        self.config = config
        self.stop_event = mp.Event()
        self.input_queue = mp.Queue(5)
        self.output_queue = mp.Queue(5)
        self.tracking_loop = _TrackingLoop(self.config, self.stop_event, self.input_queue, self.output_queue)

    def start(self):
        self.tracking_loop.start()

    def stop(self):
        self.stop_event.set()

    def put_detection(self, detection, block=True, timeout=10):
        self._assert_running()

        try:
            self.input_queue.put(detection, block, timeout)
        except queue.Full:
            raise InputFullError(f'No detection result could be added to the input queue after having waited {timeout}s')

    def get_tracking(self, block=True, timeout=10):
        self._assert_running()

        try:
            return self.output_queue.get(block, timeout)
        except queue.Empty:
            raise OutputEmptyError(f'No tracking output has been received after having waited {timeout}s')

    def _assert_running(self):
        if self.stop_event.is_set():
            raise StoppedError('Detector has already been stopped')
      

class _TrackingLoop(mp.Process):
    def __init__(self, config: ObjectTrackerConfig, stop_event, input_queue, output_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stop_event = stop_event
        self.config = config
        self.input_queue = input_queue
        self.output_queue = output_queue

        self.tracker = None


    @torch.no_grad()
    def run(self):        
        self._setup()

        while not self.stop_event.is_set():
            try:
                input_image, detection_proto = self._get_next_detection(block=False)
            except queue.Empty:
                time.sleep(0.01)
                continue

            det_array = self._prepare_detection_input(detection_proto)
            tracking_output_array = self.tracker.update(det_array, input_image)
            
            try:
                self.output_queue.put(self._create_output(tracking_output_array, detection_proto), block=False)
            except queue.Full:
                time.sleep(0.01)
        
        self.input_queue.cancel_join_thread()
        self.output_queue.cancel_join_thread()

    def _setup(self):
        self.tracker = OCSort(
            Path(self.config.tracking_params.model_weights), 
            torch.device(self.config.device), 
            self.config.tracking_params.fp16, 
            self.config.tracking_params.det_thresh,
        )

    def _get_next_detection(self, block=False):
        detection_proto_raw = self.input_queue.get(block)

        detection_proto = DetectionOutput()
        detection_proto.ParseFromString(detection_proto_raw)

        input_frame = detection_proto.frame
        input_image = np.frombuffer(input_frame.frame_data, dtype=np.uint8).reshape(input_frame.shape)

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
    
    def _create_output(self, tracking_output, detection_proto: DetectionOutput):
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

            tracked_detection.detection.confidence = float(pred[4])
            tracked_detection.detection.class_id = int(pred[5])

            tracked_detection.object_id = bytes(pred[6])


        return output_proto.SerializeToString()