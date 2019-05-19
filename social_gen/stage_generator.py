import random
from collections import Counter

from . import timers
from . import conditions

from .rules import Rule
from .stages import Stage


_TIMERS = [
    timers.DeterministicTimer,
    timers.ExponentialTimer
]
_BASIC_CONDITIONS = [
    conditions.TimeCondition,
    conditions.SequenceCondition
]

_TIME_COMPARISON_OPERATORS = ['less', 'more', 'between']
_LOGIC_OPERATORS = ['and', 'or']


def generate_stage(num_rules, max_aggregation_level, num_nodes, max_time, force_uniformness=None):
    generated_rules = []
    if force_uniformness is None:
        force_uniformness = []

    if 'agg_level' in force_uniformness:
        agg_cardinality = num_rules // (max_aggregation_level + 1)
        agg_levels = Counter({level: agg_cardinality for level in range(max_aggregation_level + 1)})
        if num_rules % (max_aggregation_level + 1) != 0:
            agg_levels[0] += 1
        agg_levels = agg_levels.elements()

    for _ in range(num_rules):
        timer = _generate_timer()

        if 'agg_level' in force_uniformness:
            condition_aggregation_level = next(agg_levels)
        else:
            condition_aggregation_level = random.randrange(max_aggregation_level + 1)

        condition = _generate_condition(
            condition_aggregation_level, num_nodes, max_time
        )

        sender_id, recipient_id = random.choices(range(num_nodes), k=2)
        rule = Rule(sender_id, recipient_id, condition, timer)
        generated_rules.append(rule)

    return Stage(generated_rules)


def _generate_timer():
    timer_class = random.choice(_TIMERS)
    if timer_class is timers.DeterministicTimer:
        timer_args = {'time': round(random.uniform(5, 10), 2)}
    elif timer_class is timers.ExponentialTimer:
        intensity = round(random.uniform(0.1, 2), 2)
        timer_args = {
            'intensity': intensity,
            'threshold': round(1 / intensity + random.uniform(1, 5), 2)
        }
    return timer_class(**timer_args)


def _generate_condition(level, num_nodes, max_time):
    if level == 0:
        return _generate_basic_condition(num_nodes, max_time)

    left_condition = _generate_condition(level - 1, num_nodes, max_time)
    if random.choice([True, False]):
        right_condition = _generate_condition(level - 1, num_nodes, max_time)
    else:
        right_condition = _generate_basic_condition(num_nodes, max_time)
        
    logic_operator = random.choice(_LOGIC_OPERATORS)
    return conditions.AggregateCondition(
        left_condition, right_condition, logic_operator
    )
    

def _generate_basic_condition(num_nodes, max_time):
    basic_condition_class = random.choice(_BASIC_CONDITIONS)
    if basic_condition_class is conditions.TimeCondition:
        bc_args = {
            'comparison_operator': random.choice(_TIME_COMPARISON_OPERATORS),
            'condition_time_1': round(random.uniform(10, max_time - 10), 2)
        }
        bc_args['condition_time_2'] = round(min(
            max_time, bc_args['condition_time_1'] + random.uniform(5, max(6, max_time / 10))), 2)
    elif basic_condition_class is conditions.SequenceCondition:
        regexp_length = random.randint(1, 3)
        bc_args = {
            'sender_regexp': _generate_random_sequence_regexp(num_nodes, regexp_length),
            'recipient_regexp': _generate_random_sequence_regexp(num_nodes, regexp_length),
            'time_regexp': [round(random.uniform(2, 10), 2) for _ in range(regexp_length)]
        }

    basic_condition = basic_condition_class(**bc_args)
    if random.choice([True, False]):
        return basic_condition
    condition_probability = round(random.uniform(0.2, 0.9), 2)
    return conditions.NonDeterministicCondition(basic_condition, condition_probability)


def _generate_random_sequence_regexp(num_nodes, regexp_length):
    return random.choices(
        population=list(range(num_nodes)) + ['?'],
        cum_weights=list(range(1, num_nodes + 1)) + [1.25 * num_nodes],
        k=regexp_length
    )
