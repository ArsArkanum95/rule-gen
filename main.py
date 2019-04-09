from timers import DeterministicTimer, ExponentialTimer
from conditions import TimeCondition, SequenceCondition
from rules import Rule
from stages import Stage


timer1 = DeterministicTimer(2)
condition1 = TimeCondition('more', 10)
rule1 = Rule(0, 1, condition1, timer1)

timer2 = ExponentialTimer(1, 3)
condition2 = SequenceCondition([0, 0], [1, 1], [5., 5.])
rule2 = Rule(0, 1, condition2, timer2)

stage = Stage([rule1, rule2])

sequence = stage.generate(20)
print(sequence)
labels = stage.analyse(sequence)
print()
print(dict(labels))