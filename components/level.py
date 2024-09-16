from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

"""
Level class:
    A component that tracks the experience and level progression of an entity,
    such as the player. It handles level-ups, stat increases, and experience
    points (XP).

Attributes:
    parent (Actor):
        The entity instance that owns this component.
    current_level (int):
        The current level of the entity.
    current_xp (int):
        The current experience points of the entity.
    level_up_base (int):
        The base amount of experience points required for a level-up.
    level_up_factor (int):
        The scaling factor applied to the experience requirement for each level.
    xp_given (int):
        The amount of experience points this entity gives when defeated.

Methods:
    experience_to_next_level (property):
        Calculates the amount of experience points needed to reach the next level.

        Return:
            > int: The experience points needed for the next level.

    requires_level_up (property):
        Checks if the entity has enough experience to level up.

        Return:
            > bool: True if the entity needs to level up, otherwise False.

    add_xp:
        Adds experience points to the entity. If the entity has enough XP to level
        up, it triggers the level-up process.

        Input:
            > xp (int): The amount of experience to add.

        Return:
            > None

    increase_level:
        Increases the entity's level and resets the experience needed for the next level.

        Return:
            > None

    increase_max_hp:
        Increases the entity's maximum health points and heals the entity by the
        same amount. Advances the level.

        Input:
            > amount (int, optional): The amount by which to increase max HP. Default is 20.

        Return:
            > None

    increase_power:
        Increases the entity's power (attack) stat. Advances the level.

        Input:
            > amount (int, optional): The amount by which to increase power. Default is 1.

        Return:
            > None

    increase_defense:
        Increases the entity's defense stat. Advances the level.

        Input:
            > amount (int, optional): The amount by which to increase defense. Default is 1.

        Return:
            > None
"""
class Level(BaseComponent):
    parent: Actor

    def __init__(
            self,
            current_level: int = 1,
            current_xp: int = 0,
            level_up_base: int = 0,
            level_up_factor: int = 150,
            xp_given: int = 0,
        ):
        self.current_level = current_level
        self.current_xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor
        self.xp_given = xp_given

    @property
    def experience_to_next_level(self) -> int:
        return self.level_up_base + self.current_level * self.level_up_factor
    
    @property
    def requires_level_up(self) -> bool:
        return self.current_xp > self.experience_to_next_level
    
    def add_xp(self, xp: int) -> None:
        if xp == 0 or self.level_up_base == 0:
            return
        
        self.current_xp += xp
        self.engine.message_log.add_message(f'You gain {xp} experience points.')

        if self.requires_level_up:
            self.engine.message_log.add_message(
                f'You advance to level {self.current_level + 1}!'
            )
        
    def increase_level(self) -> None:
        self.current_xp -= self.experience_to_next_level

        self.current_level += 1

    def increase_max_hp(self, amount: int  = 20) -> None:
        self.parent.fighter.max_hp += amount
        self.parent.fighter.hp += amount

        self.engine.message_log.add_message('Your health improves!')

        self.increase_level()
    
    def increase_power(self, amount: int = 1) -> None:
        self.parent.fighter.power += amount

        self.engine.message_log.add_message('You feel stronger!')

        self.increase_level()

    def increase_defense(self, amount: int = 1) -> None:
        self.parent.fighter.defense += amount

        self.engine.message_log.add_message('Your skin getting thicker!')

        self.increase_level()