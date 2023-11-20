from time import time


class Timer:
    _start = 0

    def start(self):
        self._start = int(time())

    def slice(self, message: str):
        print(f"{(int(time()) - self._start)}s: {message}")


timer = Timer()
