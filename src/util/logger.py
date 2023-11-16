import time

log_file_name = "timing.log"

template = "{} — {} — {}\n"


def log(message):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            with open(log_file_name, "a") as f:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                f.write(template.format(f"{round(end_time - start_time, 1)}s", message, func.__name__))
            return result
        return wrapped
    return wrapper


def async_log(message):
    def wrapper(func):
        async def wrapped(*args, **kwargs):
            with open(log_file_name, "a") as f:
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                f.write(template.format(f"{round(end_time - start_time, 1)}s", message, func.__name__))
            return result
        return wrapped
    return wrapper
