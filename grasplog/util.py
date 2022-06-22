import time


class Timer:
    def __init__(self):
        self.start_time = time.perf_counter()

    def elapsed_ms(self) -> int:
        now = time.perf_counter()
        return int((now - self.start_time) * 1000)
