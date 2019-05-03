from stage_generator import generate_stage


def run_experiments():
    duration = 100
    while True:
        stage = generate_stage(5, 0, 2, duration)

        sequence = stage.generate(duration)
        if not sequence:
            continue

        event_coverage, rule_coverage = stage.analyse(sequence, duration)

        for rule_id, rule in enumerate(stage.rules):
            rule_test_results = rule_coverage[rule_id]
            if rule_test_results is None:
                continue

            test_probability, test_p = rule_test_results
            true_probability = rule.probability
            
            print(true_probability, test_probability, test_p)

        return

run_experiments()