import random


class Rule:

    def __init__(self, sender_id, recipient_id, condition, timer):
        self._sender_id = sender_id
        self._recipient_id = recipient_id

        self._condition = condition
        self._timer = timer

        self._last_succ_test_id = 0
        self._covered_tests_count = 0

    @property
    def sender_id(self):
        return self._sender_id

    @property
    def recipient_id(self):
        return self._recipient_id

    @property
    def probability(self):
        return self._condition.probability * self._timer.probability

    @property
    def covered_tests_count(self):
        return self._covered_tests_count

    def produce_event(self, *, current_time, **kwargs):
        if self._condition(current_time=current_time, **kwargs):
            time = self._timer(current_time)
            if time is not False and random.random() <= self._condition.probability:
                return self._sender_id, self._recipient_id, current_time + time
        return False

    def test_condition(self, *, current_time, **kwargs):
        if self._condition(
            current_time=current_time, **kwargs) and \
           self._timer.is_ready(current_time):
            self._timer.start_timeout(current_time)
            self._last_succ_test_id += 1
            return True, self._last_succ_test_id
        return False, 0

    def increment_activation_count(self):
        self._covered_tests_count += 1

    def reset_timer(self):
        self._timer.reset_timeout()

    def get_timer_bounds(self, current_time):
        start, end = self._timer.get_bounds()
        return start + current_time, end + current_time
