from typing import TextIO
import time
import pybase64

from objecttracker.config import ObjectTrackerConfig
from objecttracker.tracker import Tracker

from save_annotated_frames import save_as_image

from benchmarks.plot import plot_time, plot_time_num_cars
from benchmarks.analyse import analyse_csv

from visionlib.pipeline.publisher import RedisPublisher
from prometheus_client import Histogram

import sys
sys.path.insert(1, '../vision-pipeline-k8s/tools')
from common import MESSAGE_SEPARATOR, DumpMeta, Event



def read_messages(file: TextIO):
    buffer = ''
    while True:
        chunk = file.read(4096)
        if len(chunk) == 0:
            break
        sep_idx = chunk.find(MESSAGE_SEPARATOR)
        if sep_idx != -1:
            yield buffer + chunk[:sep_idx]
            buffer = chunk[sep_idx+1:]
        else:
            buffer += chunk

def init_output(sw_version, file_name):
    with open(f'benchmarks/{sw_version}/{file_name}.csv','a') as fd:
        fd.write("Frame,num_cars,time_in_us\n")

def log_frame(sw_version, file_name):
    #write data to csv_file
    with open(f'benchmarks/{sw_version}/{file_name}.csv','a') as fd:
        fd.write(f'{counter}, {num_cars}, {inference_time}\n')


if __name__ == '__main__':
    timer = time.time()
    CONFIG = ObjectTrackerConfig()

    publish = RedisPublisher(CONFIG.redis.host, CONFIG.redis.port)

    REDIS_PUBLISH_DURATION = Histogram('object_tracker_redis_publish_duration', 'The time it takes to push a message onto the Redis stream',
                                   buckets=(0.0025, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25))
    

    chosen_tracker = "deepocsort"
    sw_version = "original_script"
    file_name = "0-7_cores"

    tracker = Tracker(CONFIG, chosen_tracker)

    frame_counter = 0

    save_frame_images = False
    bench = False

    if bench:
        init_output(sw_version, file_name)


    #with publish, open("../vision-pipeline-k8s/tools/2023-12-13T12-22-43+0100.saedump", 'r') as input_file:
    with publish, open("../vision-pipeline-k8s/tools/2024-01-10T16-45-03+0100.saedump", 'r') as input_file:
        
            message_reader = read_messages(input_file)

            playback_start = time.time()
            start_message = next(message_reader)
            dump_meta = DumpMeta.model_validate_json(start_message)


            for message in message_reader:
                
                if frame_counter == 355:
                    break

                event = Event.model_validate_json(message)
                proto_bytes = pybase64.standard_b64decode(event.data_b64)

                output_proto_data, num_cars, inference_time = tracker.get(proto_bytes)

                frame_counter += 1
                print(frame_counter)
                
                if bench:
                    log_frame(sw_version, file_name)
            
                #with REDIS_PUBLISH_DURATION.time():
                    #publish(f'{CONFIG.redis.output_stream_prefix}:{"test_stream"}', output_proto_data)   
                
                if save_frame_images:
                    save_as_image(f"benchmarks/{sw_version}/frames_new/", output_proto_data, frame_counter)
                    
    if bench:
        plot_time(sw_version, file_name)
        plot_time_num_cars(sw_version, file_name)
        analyse_csv(sw_version, file_name)
    