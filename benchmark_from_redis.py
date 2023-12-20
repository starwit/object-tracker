import logging
import signal
import threading
import subprocess
import time
import sys

from prometheus_client import Histogram
from visionlib.pipeline.consumer import RedisConsumer
from visionlib.pipeline.publisher import RedisPublisher

from objecttracker.config import ObjectTrackerConfig
from objecttracker.tracker import Tracker

FRAME_COUNTER = 0

REDIS_PUBLISH_DURATION = Histogram('object_tracker_redis_publish_duration', 'The time it takes to push a message onto the Redis stream',
                                   buckets=(0.0025, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25))

if __name__ == '__main__':

    # Load config from settings.yaml / env vars
    CONFIG = ObjectTrackerConfig()

    # Init Detector
    tracker = Tracker(CONFIG)

    consume = RedisConsumer(CONFIG.redis.host, CONFIG.redis.port, 
                            stream_keys=[f'{CONFIG.redis.input_stream_prefix}:{CONFIG.redis.stream_id}'])

    publish = RedisPublisher(CONFIG.redis.host, CONFIG.redis.port)

    # start play.py script in subprocess to ensure always starting with first frame
    #venv = '../venv/bin/python'

    #playpy = '../vision-pipeline-k8s/tools/play.py'

    #dump_file = '../vision-pipeline-k8s/tools/2023-12-13T12-22-43+0100.saedump'

    #subprocess.Popen([venv, playpy, '-i', dump_file])
    #time.sleep(1)

    with consume, publish:
        for stream_id, proto_data in consume():

            if stream_id is not None:
                print(stream_id)
           
                # tracker gets proto data from redis consumer
                output_proto_data = tracker.get(proto_data)

                #FRAME_COUNTER += 1
                #print(FRAME_COUNTER)

                #if output_proto_data is None:
                  #  continue
                
                #with REDIS_PUBLISH_DURATION.time():
                    #publish(f'{CONFIG.redis.output_stream_prefix}:{stream_id}', output_proto_data)   
            
            else:
                 print("no stream")
            