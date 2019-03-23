class Stage:
    def __init__(self, rules, duration, step=1):
        self._rules = rules
        self._duration = duration
        self._step = step

    def generate(self):
        current_time = 0.
        generated_sequence = []

        while current_time < self._duration:
            new_current_time = current_time + self._step
            new_events = []

            for rule in self._rules:
                result = rule(current_time=current_time, sequence=generated_sequence)
                if result:
                    new_events.append(result)

            if new_events:
                generated_sequence.extend(sorted(new_events, key=lambda e: e[2]))
                last_event_time = generated_sequence[-1][2]

                if last_event_time < new_current_time:
                    new_current_time = last_event_time

            current_time = new_current_time
            

        return generated_sequence