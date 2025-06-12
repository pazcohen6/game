from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

"""
Level class:
    A component that tracks the experience and level progression of an entity,
    such as the player. It handles leveling up, stat increases, and experience
    point (XP) management.

Attributes:
    parent (Actor):
        The entity instance that owns this component.
    current_level (int):
        The current level of the entity.
    current_xp (int):
        The current experience points of the entity.
    level_up_base (int):
        The base amount of experience required for the first level-up.
    level_up_factor (int):
        The scaling factor applied to the XP requirement for each subsequent level.
    xp_given (int):
        The amount of XP this entity gives when defeated.

Properties:
    experience_to_next_level:
        Calculates the amount of XP required to reach the next level.

        Returns:
            > int: The XP required to reach the next level.

    requires_level_up:
        Checks if the entity has enough XP to level up.

        Returns:
            > bool: True if the entity is ready to level up, otherwise False.

Methods:
    add_xp:
        Adds experience points to the entity. If enough XP is gained,
        it announces the level-up.

        Parameters:
            xp (int): The amount of XP to add.

        Returns:
            > None

    increase_level:
        Increases the entity's level and reduces the XP accordingly.

        Returns:
            > None

    increase_strength:
        Increases the entity's strength. May also increase max HP if the new
        agility value does not divide evenly by 5.

        Parameters:
            amount (int, optional): The amount to increase strength by. Default is 1.

        Returns:
            > None

    increase_agility:
        Increases the entity's agility. Triggers different messages based on thresholds.

        Parameters:
            amount (int, optional): The amount to increase agility by. Default is 1.

        Returns:
            > None

    increase_max_hp:
        Increases the entity's maximum HP and heals it by the same amount.

        Parameters:
            amount (int, optional): The amount to increase max HP by. Default is 5.

        Returns:
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

    def increase_strength(self, amount: int = 1) -> None:
        self.parent.fighter.base_strength += amount
        
        if self.parent.fighter.base_strength % 5 != 0 :
            self.increase_max_hp()
        else :
            self.engine.message_log.add_message('You feel stronger!')
        self.increase_level()

    def increase_agility(self, amount: int = 1) -> None:
        self.parent.fighter.base_agility += amount
        
        if self.parent.fighter.base_agility % 5 != 0 :
            self.engine.message_log.add_message('You feel a deadly precision rising within you!')
        else :
            self.engine.message_log.add_message('Your skin is getting thicker!') 
        self.increase_level()

    def increase_max_hp(self, amount: int  = 5) -> None:
        self.parent.fighter.max_hp += amount
        self.parent.fighter.hp += amount

        self.engine.message_log.add_message('Your health improves!')
        self.increase_level()