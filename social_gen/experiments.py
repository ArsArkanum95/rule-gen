import numpy as np

from .stages import Stage
from .stage_generator import generate_stage


def run_experiments(duration, stage, generator=None):
    while True:
        if generator:
            sequence = generator()
        else:
            sequence = stage.generate(duration)

        if not sequence:
            continue

        event_coverage, rule_coverage = stage.analyse(sequence, duration)
        print(event_coverage)

        res = []

        for rule_id, rule in enumerate(stage.rules):
            rule_test_results = rule_coverage[rule_id]
            if rule_test_results is None:
                continue

            test_probability, test_p = rule_test_results
            true_probability = rule.probability
            
            res.append((abs(true_probability - test_probability), test_p))

        probabilities_difference, test_p_values = list(zip(*res))

        probabilities_difference = np.array(probabilities_difference)
        test_p_values = np.array(test_p_values)

        print(probabilities_difference.mean(), probabilities_difference.std(), test_p_values.mean(), test_p_values.std())
        return

stage = generate_stage(
    num_rules=20,
    max_aggregation_level=0,
    num_nodes=2,
    max_time=1000
)

# import copy
# stage2 = copy.deepcopy(stage)
# stage2.rules.pop()
# stage2.rules.pop()
# stage2.rules.pop()
# stage2.rules.pop()
#print(len(stage.rules), len(stage2.rules))

run_experiments(
    1000,
    stage,
    lambda: list(zip([0] * 9000, [1] * 9000, range(0, 900, 1)))
)
