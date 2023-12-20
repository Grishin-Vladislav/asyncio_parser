import time
from functools import wraps


def async_timer(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        value = await f(*args, **kwargs)
        run_time = time.time() - start_time
        print(f'Finished {f.__name__!r} in {run_time:.4f} secs')
        return value
    return wrapper
