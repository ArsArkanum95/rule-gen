class Rule:
    def __init__(self, sender_id, recipient_id, condition, timer):
        self._sender_id = sender_id
        self._recipient_id = recipient_id

        self._condition = condition
        self._timer = timer

    @property
    def sender_id(self):
        return self._sender_id

    @property
    def recipient_id(self):
        return self._recipient_id

    @property
    def probability(self):
        return self._condition.probability

    def produce_event(self, *, current_time, **kwargs):
        if self._condition(current_time=current_time, **kwargs):
            time = self._timer(current_time)
            if time:
                return self._sender_id, self._recipient_id, current_time + time
        return False

    def test_condition(self, *, current_time, **kwargs):
        if self._condition.call_deterministic(
            current_time=current_time, **kwargs) and \
           self._timer.is_ready(current_time):
            self._timer.start_timeout(current_time)
            return True
        return False    

    def reset_timer(self):
        self._timer.reset_timeout()

    def get_timer_bounds(self, current_time):
        start, end = self._timer.get_bounds()
        return start + current_time, end + current_time
