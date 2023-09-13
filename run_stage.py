import signal
import threading

from visionlib.pipeline.consumer import RedisConsumer
from visionlib.pipeline.publisher import RedisPublisher

from objecttracker.config import ObjectTrackerConfig
from objecttracker.tracker import Tracker

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

    # Init Detector
    tracker = Tracker(CONFIG)

    consume = RedisConsumer(CONFIG.redis.host, CONFIG.redis.port, 
                            stream_keys=[f'{CONFIG.redis.input_stream_prefix}:{CONFIG.redis.stream_id}'])
    publish = RedisPublisher(CONFIG.redis.host, CONFIG.redis.port)

    with consume, publish:
        for stream_id, proto_data in consume():
            if stream_id is None:
                continue

            output_proto_data = tracker.get(proto_data)

            if output_proto_data is None:
                continue

            publish(f'{CONFIG.redis.output_stream_prefix}:{stream_id}', proto_data)

            if stop_event.is_set():
                break