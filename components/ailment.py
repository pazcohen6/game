#from entity import Actor
from components.fighter import Fighter
"""
    TODO
"""
class Ailment():
    target: Fighter
    duration: int

    def __init__(self, fighter: Fighter, duration: int ) -> None:
        self.target = fighter
        self.duration = duration

    def perform(self) -> None:
        self.duration -= 1
        if self.duration <= 0:
            self.target.ailments.remove(self) # TODO check
        pass

"""
    TODO
"""
class BurningAilment(Ailment):
    pass  #TODO

    def perform(self) -> None:
        self.target.take_damage(amount = 1)