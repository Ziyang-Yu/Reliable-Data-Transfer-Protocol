import time

from threading import Timer


class Timer:

    def __init__(self, func=time.perf_counter):
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError('Already started')
        self._start = self._func()

    def elapsed(self):
        if self._start is None:
            raise RuntimeError('Not started')
        return self._func() - self._start


class RepeatTimer(Timer):

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
