from stage_generator import generate_stage


def run_experiments(*, duration, **stage_gen_kwargs):
    while True:
        stage = generate_stage(max_time=duration, **stage_gen_kwargs)

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
            
            res.append((true_probability, test_probability, test_p))

        true_probabilities, test_probabilities, test_p_values = list(zip(*res))
        return

run_experiments(
    num_rules=10,
    max_aggregation_level=0,
    num_nodes=2,
    duration=100
)
