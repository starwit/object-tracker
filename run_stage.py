import signal
import redis
import threading
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

    # Init output
    redis_conn = redis.Redis(
        host=CONFIG.redis.host,
        port=CONFIG.redis.port,
    )

    # Start processing images
    while not stop_event.is_set():
        input_okay = False
        while not input_okay:
            result = redis_conn.xread(
                count=1,
                block=5000,
                streams={f'object_detector_{CONFIG.redis.detector_id}': '$' if last_retrieved_id is None else last_retrieved_id}
            )
        
            if result is None or len(result) == 0:
                continue

            # These unpacking incantations are apparently necessary...
            last_retrieved_id = result[0][1][0][0].decode('utf-8')
            input_proto = result[0][1][0][1][b'proto_data']

            input_okay = True

        output_proto = tracker.get(input_proto)

        if output_proto is not None:
            redis_conn.xadd(name=f'object_detector', fields={'proto_data': output_proto}, maxlen=10)
