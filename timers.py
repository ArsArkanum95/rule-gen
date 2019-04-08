import abc
import random


class AbstractTimer(abc.ABC):
    @abc.abstractmethod
    def __init__(self, ready_timeout):
        self._start_time = None
        self._ready_timeout = ready_timeout

    def is_ready(self, current_time):
        return not (self._start_time is not None and \
               current_time - self._start_time < self._ready_timeout)

    def start_timeout(self, current_time):
        self._start_time = current_time

    def reset_timeout(self):
        self._start_time = None

    def _call_if_ready(self, current_time, return_func):
        if not self.is_ready(current_time):
            return False

        self.start_timeout(current_time)
        return return_func()

    @abc.abstractmethod
    def get_bounds(self):
        pass

class DeterministicTimer(AbstractTimer):
    def __init__(self, time):
        super().__init__(time)
        self._time = time

    def __call__(self, current_time):
        return self._call_if_ready(
            current_time, lambda: self._time)

    def get_bounds(self):
        return self._time, self._time


class ExponentialTimer(AbstractTimer):
    def __init__(self, intensity, threshold):
        super().__init__(threshold)
        self._intensity = intensity
        self._threshold = threshold

    def __call__(self, current_time):
        return self._call_if_ready(
            current_time, self._draw_time)

    def get_bounds(self):
        return 0., self._threshold

    def _draw_time(self):
        time = random.expovariate(self._intensity) 
        return time if time <= self._threshold else False
