import logging
import signal
import threading

from prometheus_client import Counter, Histogram, start_http_server
from visionlib.pipeline.consumer import RedisConsumer
from visionlib.pipeline.publisher import RedisPublisher

from objecttracker.config import ObjectTrackerConfig
from objecttracker.tracker import Tracker

logger = logging.getLogger(__name__)

PROMETHEUS_METRICS_PORT = 8000

REDIS_PUBLISH_DURATION = Histogram('object_tracker_redis_publish_duration', 'The time it takes to push a message onto the Redis stream',
                                   buckets=(0.0025, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25))
FRAME_COUNTER = Counter('object_tracker_frame_counter', 'How many frames have been consumed from the Redis input stream')

if __name__ == '__main__':

    stop_event = threading.Event()
    last_retrieved_id = None

    # Register signal handlers
    def sig_handler(signum, _):
        signame = signal.Signals(signum).name
        print(f'Caught signal {signame} ({signum}). Exiting...')
        stop_event.set()

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # Load config from settings.yaml / env vars
    CONFIG = ObjectTrackerConfig()

    logger.setLevel(CONFIG.log_level.value)

    logger.info(f'Starting prometheus metrics endpoint on port {PROMETHEUS_METRICS_PORT}')

    start_http_server(PROMETHEUS_METRICS_PORT)

    logger.info(f'Starting object tracker stage. Config: {CONFIG.model_dump_json(indent=2)}')

    # Init Tracker
    tracker = Tracker(CONFIG, "deepocsort_og")

    consume = RedisConsumer(CONFIG.redis.host, CONFIG.redis.port, 
                            stream_keys=[f'{CONFIG.redis.input_stream_prefix}:{CONFIG.redis.stream_id}'])
    publish = RedisPublisher(CONFIG.redis.host, CONFIG.redis.port)

    with consume, publish:
        for stream_id, proto_data in consume():
            if stop_event.is_set():
                break
            
            if stream_id is None:
                continue

            FRAME_COUNTER.inc()

            output_proto_data, num_cars, inference_time, tracking_output = tracker.get(proto_data)

            if output_proto_data is None:
                continue
            
            with REDIS_PUBLISH_DURATION.time():
                publish(f'{CONFIG.redis.output_stream_prefix}:{stream_id}', output_proto_data)