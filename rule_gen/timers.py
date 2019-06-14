import abc
import math
import random


class AbstractTimer(abc.ABC):
    def __init__(self, ready_timeout, probability=1.0):
        self._start_time = None
        self._ready_timeout = ready_timeout
        self._probability = probability

    @abc.abstractmethod
    def __str__(self):
        return ''

    @abc.abstractmethod
    def __call__(self):
        pass

    @abc.abstractmethod
    def get_bounds(self):
        pass

    @property
    def probability(self):
        return self._probability

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


class DeterministicTimer(AbstractTimer):
    def __init__(self, time):
        super().__init__(time)
        self._time = time

    def __str__(self):
        return f'DeterministicTimer: time - {self._time}'

    def __call__(self, current_time):
        return self._call_if_ready(
            current_time, lambda: self._time)

    def get_bounds(self):
        return self._time, self._time


class ExponentialTimer(AbstractTimer):
    def __init__(self, intensity, threshold, rounding=2):
        probability = 1 - math.exp(-intensity * threshold)
        super().__init__(threshold, probability)
        self._intensity = intensity
        self._threshold = threshold
        self._rounding = rounding

        self._min_time = pow(10, -rounding)

    def __str__(self):
        return f'ExponentialTimer: int - {self._intensity}, thr - {self._threshold}'

    def __call__(self, current_time):
        time = self._call_if_ready(current_time, self._draw_time)
        if time is not False:
            return round(time, self._rounding)
        return False

    def get_bounds(self):
        return self._min_time, self._threshold

    def _draw_time(self):
        time = max(self._min_time, random.expovariate(self._intensity))
        return time if time <= self._threshold else False
