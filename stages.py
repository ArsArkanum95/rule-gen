from collections import defaultdict
from itertools import takewhile


class Stage:
    def __init__(self, rules, step=1):
        self._rules = rules
        self._step = step

    def generate(self, duration):
        self._reset_all_rules()

        current_time = 0.
        generated_sequence = []
        new_events_buffer = []

        while current_time < duration:
            last_event_time = None

            for rule in self._rules:
                result = rule.produce_event(
                    current_time=current_time, sequence=generated_sequence)
                if result:
                    new_events_buffer.append(result)

            # TODO this is slow 
            if new_events_buffer:
                new_events_buffer.sort(key=lambda e: e[2])

            if new_events_buffer and new_events_buffer[0][2] <= current_time:
                accepted_events = list(takewhile(lambda e: e[2] <= current_time,
                                                 new_events_buffer))
                generated_sequence.extend(accepted_events)
                new_events_buffer = new_events_buffer[len(accepted_events):]
            
            if new_events_buffer:
                last_event_time = new_events_buffer[0][2]

            current_time = self._get_next_time(current_time, last_event_time)
            
        return generated_sequence

    def analyse(self, sequence):
        self._reset_all_rules()

        event_labels = defaultdict(list)
        expected_events = self._get_next_expected_events(0., [])

        current_event_id = 0
        current_time = 0.

        while current_event_id < len(sequence):
            current_event = sequence[current_event_id]
            current_event_time = current_event[2]

            if current_time == current_event_time:
                new_labels, filtered_expected_events = \
                    self._process_expected_events(
                        expected_events, current_event, current_time)
                event_labels[current_event_id].extend(new_labels)
                expected_events = filtered_expected_events

                current_event_id += 1

            current_history = sequence[:current_event_id]
            expected_events.extend(
                self._get_next_expected_events(
                    current_time, current_history))

            # current_event_time could have changed due to new current_event(_id)
            if current_event_id < len(sequence):
                current_event_time = sequence[current_event_id][2]

            current_time = self._get_next_time(current_time, current_event_time)

        return event_labels

    def _reset_all_rules(self):
        for rule in self._rules:
            rule.reset_timer()

    def _get_next_time(self, current_time, potential_next_time=None):
        next_time = (current_time + self._step) // self._step * self._step
        if potential_next_time is not None and potential_next_time < next_time:
            return potential_next_time
        return next_time

    def _process_expected_events(self, expected_events, event, current_time):
        new_labels = []
        filtered_expected_events = []

        current_sender_id, current_recipient_id, _ = event

        for exp_event in expected_events:
            rule, start_time, end_time = exp_event

            if current_time > end_time:
                continue

            if rule.sender_id == current_sender_id and \
               rule.recipient_id == current_recipient_id and \
               start_time <= current_time <= end_time:
                new_labels.append(rule)

            filtered_expected_events.append(exp_event)

        return new_labels, filtered_expected_events

    def _get_next_expected_events(self, current_time, current_sequence):
        expected_events = []

        for rule in self._rules:
            rule_activated = rule.test_condition(
                current_time=current_time, sequence=current_sequence
            )
            if rule_activated:
                expected_events.append((
                    rule,
                    *rule.get_timer_bounds(current_time)
                ))

        return expected_events
