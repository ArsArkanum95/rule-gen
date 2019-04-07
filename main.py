from timers import DeterministicTimer
from conditions import TimeCondition
from rules import Rule
from stages import Stage


timer = DeterministicTimer(2)
condition = TimeCondition('more', 10)
rule = Rule(0, 1, condition, timer)

stage = Stage([rule])

sequence = stage.generate(20)
print(sequence)