from collections import defaultdict
from itertools import takewhile

from scipy.stats import binom_test


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
            if new_events_buffer and new_events_buffer[0][2] <= current_time:
                accepted_events = list(takewhile(lambda e: e[2] <= current_time,
                                                 new_events_buffer))
                generated_sequence.extend(accepted_events)
                new_events_buffer = new_events_buffer[len(accepted_events):]

            for rule in self._rules:
                result = rule.produce_event(
                    current_time=current_time, sequence=generated_sequence)
                if result:
                    new_events_buffer.append(result)

            last_event_time = None

            # TODO this is slow
            if new_events_buffer:
                new_events_buffer.sort(key=lambda e: e[2])
                last_event_time = new_events_buffer[0][2]

            current_time = self._get_next_time(current_time, last_event_time)
            
        return generated_sequence

    def analyse(self, sequence, duration=None):
        self._reset_all_rules()
        if duration is None:
            duration = sequence[-1][2]

        event_labels = defaultdict(list)
        expected_events = self._get_next_expected_events(0., [], duration)

        current_event_id = 0
        current_time = 0.

        while current_event_id < len(sequence):
            current_event = sequence[current_event_id]
            current_event_time = current_event[2]

            if current_time == current_event_time:
                new_labels, filtered_expected_events = \
                    self._process_expected_events(
                        expected_events,current_event, current_time)
                event_labels[current_event_id].extend(new_labels)
                expected_events = filtered_expected_events

                current_event_id += 1

            current_history = sequence[:current_event_id]
            expected_events.extend(
                self._get_next_expected_events(
                    current_time, current_history, duration))

            # current_event_time could have changed due to new current_event(_id)
            if current_event_id < len(sequence):
                current_event_time = sequence[current_event_id][2]

            current_time = self._get_next_time(current_time, current_event_time)

        num_events_covered, rules_activation_stats = self._calculate_analysis_statistics(event_labels)
        return num_events_covered / len(sequence), rules_activation_stats

    def _reset_all_rules(self):
        for rule in self._rules:
            rule.reset_state()

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
            rule_id, activation_id, start_time, end_time = exp_event

            if current_time > end_time:
                continue

            rule = self._rules[rule_id]
            if rule.sender_id == current_sender_id and \
               rule.recipient_id == current_recipient_id and \
               start_time <= current_time <= end_time:
                new_labels.append((rule_id, activation_id))

            filtered_expected_events.append(exp_event)

        return new_labels, filtered_expected_events

    def _get_next_expected_events(self, current_time, current_sequence, seq_duration):
        expected_events = []

        for rule_id, rule in enumerate(self._rules):
            rule_activated, activation_id = rule.test_condition(
                current_time=current_time, sequence=current_sequence
            )
            if rule_activated:
                start_time, end_time = rule.get_timer_bounds(current_time)
                if end_time <= seq_duration:
                    rule.increment_activation_count()
                expected_events.append((
                    rule_id,
                    activation_id,
                    start_time, end_time
                ))

        return expected_events

    def _calculate_analysis_statistics(self, labels):
        events_done = set()
        labels_done = set()

        def mark_label_done(event_id, rule_info):
            events_done.add(event_id)
            labels_done.add(rule_info)

        rest_labels = labels.items()
        while rest_labels:
            new_rest_labels = []
            work_done = False

            for event_id, fitting_rules in rest_labels:
                filtered_rules = list(filter(
                    lambda rule_info: rule_info not in labels_done,
                    fitting_rules
                ))

                if len(filtered_rules) == 1:
                    mark_label_done(event_id, filtered_rules[0])
                    work_done = True
                elif len(filtered_rules) > 1:
                    new_rest_labels.append((event_id, filtered_rules))

            if not work_done:
                most_certain_label = max(
                    new_rest_labels,
                    key=self._calculate_rules_prob_diff
                )
                most_certain_rule_info = max(
                    most_certain_label[1],
                    key=lambda ri: self._rules[ri[0]].probability
                )
                new_rest_labels.remove(most_certain_label)
                mark_label_done(most_certain_label[0], most_certain_rule_info)

            rest_labels = new_rest_labels

        return len(events_done), self._calculate_rules_activation_stats(labels_done)

    def _calculate_rules_activation_stats(self, labels):
        result = defaultdict(lambda: 0)
        for rule_id, _ in labels:
            result[rule_id] += 1

        for rule_id, rule in enumerate(self._rules):
            num_total = rule.covered_tests_count
            if num_total == 0:
                result[rule_id] = None
                continue

            num_of_hits = min(num_total, result[rule_id])
            result[rule_id] = [
                num_of_hits / num_total,
                binom_test(num_of_hits, num_total, rule.probability)
            ]

        return dict(result)

    def _calculate_rules_prob_diff(self, label):
        probabilities = [self._rules[rule_info[0]].probability for rule_info in label[1]]
        p1 = max(probabilities)
        probabilities.remove(p1)
        p2 = max(probabilities)
        return p1 - p2
