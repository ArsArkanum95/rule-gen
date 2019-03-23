class TimeCondition:
    def __init__(self, comparison_operator, condition_time_1, condition_time_2=None):
        self._comparison_operator = comparison_operator
        self._condition_time_1 = condition_time_1
        self._condition_time_2 = condition_time_2

    def __call__(self, *, current_time, **kwargs):
        if self._comparison_operator == 'less':
            return current_time < self._condition_time_1
        if self._comparison_operator == 'more':
            return current_time > self._condition_time_1
        if self._comparison_operator == 'between' and self._condition_time_2:
            return self._condition_time_1 < current_time < self._condition_time_2

class SequenceCondition:
    def __init__(self, sender_regexp, recipient_regexp, time_regexp):
        assert len(sender_regexp) == len(recipient_regexp) == len(time_regexp)

        self._sender_regexp = sender_regexp
        self._recipient_regexp = recipient_regexp
        self._time_regexp = time_regexp

    def __call__(self, *, sequence, reversed=True, **kwargs):
        sender_regexp = self._sender_regexp
        recipient_regexp = self._recipient_regexp
        time_regexp = self._time_regexp

        if reversed:
            sequence = reversed(sequence)
            sender_regexp = reversed(sender_regexp)
            recipient_regexp = reversed(recipient_regexp)
            time_regexp = reversed(time_regexp)

        state = 0
        last_time = sequence[0][2]

        for event_id, (sender, recipient, time) in enumerate(sequence):
            if time_regexp[state] <= time - last_time:
                if (sender_regexp[state] == '?' or sender_regexp[state] == sender) and \
                (recipient_regexp[state] == '?' or recipient_regexp[state] == recipient):
                    state += 1
            else:
                state = 0

            last_time = time

            if state == len(sender_regexp):
                return True#, event_id

        return False#, event_id

class AggregateCondition:
    def __init__(self, condition_1, condition_2, logic_operator='and'):
        self._condition_1 = condition_1
        self._condition_2 = condition_2
        self._logic_operator = logic_operator

    def __call__(self, **kwargs):
        evaluation_1 = self._condition_1(**kwargs)
        evaluation_2 = self._condition_2(**kwargs)

        if self._logic_operator == 'and':
            return evaluation_1 and evaluation_2
        if self._logic_operator == 'or':
            return evaluation_1 or evaluation_2