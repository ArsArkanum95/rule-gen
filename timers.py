import random


class DeterministicTimer:
    def __init__(self, time):
        self._time = time

    def __call__(self):
        return self._time

class ExponentialTimer:
    def __init__(self, intensity, threshold):
        self._intensity = intensity
        self._threshold = threshold

    def __call__(self):
        time = random.expovariate(self._intensity) 
        return time if time <= self._threshold else False
