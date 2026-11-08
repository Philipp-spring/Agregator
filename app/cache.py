import time

_seats_cache: dict = {}
CACHE_TTL = 30


def get_cached_seats(event_id):
    if event_id in _seats_cache:
        data, timestamp = _seats_cache[event_id]
        if time.time() - timestamp < CACHE_TTL:
            return data
        del _seats_cache[event_id]
    return None


def set_cached_seats(event_id, data):
    _seats_cache[event_id] = (data, time.time())
