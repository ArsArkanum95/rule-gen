import abc


class AbstractCondition(abc.ABC):
    @property
    def probability(self):
        return 1.

    @abc.abstractmethod
    def __call__(self, **kwargs):
        pass

class TimeCondition(AbstractCondition):
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


class SequenceCondition(AbstractCondition):
    def __init__(self, sender_regexp, recipient_regexp, time_regexp):
        assert len(sender_regexp) == len(recipient_regexp) == len(time_regexp) > 0

        self._sender_regexp = sender_regexp
        self._recipient_regexp = recipient_regexp
        self._time_regexp = time_regexp

    def __call__(self, *, sequence, reversed_=True, **kwargs):
        if not sequence:
            return False

        sender_regexp = self._sender_regexp
        recipient_regexp = self._recipient_regexp
        time_regexp = self._time_regexp

        if reversed_:
            sequence = list(reversed(sequence))
            sender_regexp = list(reversed(sender_regexp))
            recipient_regexp = list(reversed(recipient_regexp))
            time_regexp = list(reversed(time_regexp))

        state = 0
        last_time = None

        for sender, recipient, time in sequence:
            if last_time is None or abs(time - last_time) <= time_regexp[state]:
                if (sender_regexp[state] == '?' or sender_regexp[state] == sender) and \
                (recipient_regexp[state] == '?' or recipient_regexp[state] == recipient):
                    state += 1
            else:
                state = 0

            last_time = time

            if state == len(sender_regexp):
                return True

        return False


class AggregateCondition(AbstractCondition):
    def __init__(self, condition_1, condition_2, logic_operator='and'):
        self._condition_1 = condition_1
        self._condition_2 = condition_2
        self._logic_operator = logic_operator

    def __call__(self, **kwargs):
        if self._logic_operator == 'and':
            return self._condition_1(**kwargs) and self._condition_2(**kwargs)
        if self._logic_operator == 'or':
            return self._condition_1(**kwargs) or self._condition_2(**kwargs)


class NonDeterministicCondition(AbstractCondition):
    def __init__(self, condition, probability):
        self._condition = condition
        self._probability = probability

    @property
    def probability(self):
        return self._probability

    def __call__(self, **kwargs):
        return self._condition(**kwargs)
