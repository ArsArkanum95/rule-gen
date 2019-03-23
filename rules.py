class Rule:
    def __init__(self, sender_id, recipient_id, condition, timer):
        self._sender_id = sender_id
        self._recipient_id = recipient_id

        self._condition = condition
        self._timer = timer

    def __call__(self, *, current_time, **kwargs):
        if self._condition(current_time=current_time, **kwargs):
            time = self._timer()
            if time:
                return self._sender_id, self._recipient_id, current_time + time
        return False
