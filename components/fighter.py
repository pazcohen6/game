from __future__ import annotations

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent
from render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor
    
"""
Fighter class:
    A component that adds combat-related attributes and behaviors to an entity,
    such as health points (HP), defense, power, and critical hit chance. It also handles damage,
    death, and combat interactions.

Attributes:
    parent (Actor):
        The entity instance that owns this component.
    max_hp (int):
        The maximum health points of the entity.
    _hp (int):
        The current health points of the entity.
    base_defense (int):
        The base defense value that reduces incoming damage.
    base_power (int):
        The base attack power of the entity.
    base_critical_chance (int):
        The base chance for a critical hit.
    base_strength (int):
        The base strength value, contributing to power.
    base_agility (int):
        The base agility value, contributing to defense and critical chance.

Properties:
    hp:
        Getter and setter for the entity's current health points.
        The setter ensures HP stays within valid bounds and triggers death
        if HP reaches zero.

        Returns:
            > int: The current health points of the entity.

    defense:
        Calculates total defense, including bonuses from equipment and agility.

        Returns:
            > int: The sum of base defense, equipment bonus, and agility bonus.

    power:
        Calculates total power, including bonuses from equipment and strength.

        Returns:
            > int: The sum of base power, equipment bonus, and strength bonus.

    critical_chance:
        Calculates total critical hit chance, including bonuses from equipment and agility.

        Returns:
            > int: The total critical hit chance.

    defense_bonus:
        Retrieves the defense bonus from equipped items.

        Returns:
            > int: Defense bonus from equipment, or 0 if none.

    power_bonus:
        Retrieves the power bonus from equipped items.

        Returns:
            > int: Power bonus from equipment, or 0 if none.

    critical_chance_bonus:
        Retrieves the critical chance bonus from equipped items.

        Returns:
            > int: Critical chance bonus from equipment, or 0 if none.

Methods:
    die:
        Handles the entity's death. Updates the entity's state to represent
        a corpse, logs a death message, and triggers the game over event if
        the player dies.

        Returns:
            > None

    heal:
        Restores health points to the entity, up to max HP.

        Parameters:
            amount (int): The amount of health to restore.

        Returns:
            > int: The amount of HP actually recovered.

    take_damage:
        Reduces the entity's current health points by the given amount and checks
        if the entity should die.

        Parameters:
            amount (int): The amount of damage taken.

        Returns:
            > None
"""
class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, base_defense: int, base_power: int, critical_chance: int, 
                 strength: int = 0, agility: int = 0):
        self.max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power
        self.base_critical_chance = critical_chance
        self.base_strength = strength
        self.base_agility = agility

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))

        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus + (self.base_agility // 5)
    
    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus + (self.base_strength // 5)
    
    @property
    def critical_chance(self) ->int:
        return self.base_critical_chance + self.critical_chance_bonus + (self.base_agility - (self.base_agility // 5)) * 2
    
    @property
    def defense_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.defense_bonus
        else:
            return 0
        
    @property
    def power_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.power_bonus
        else:
            return 0
    
    @property
    def critical_chance_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.critical_chance_bonus
        else:
            return 0

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You Died"
            death_message_color = color.player_die
        else:
            death_message = f"you've defeated {self.parent.name}"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191,0,0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

        self.engine.player.level.add_xp(self.parent.level.xp_given)

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0
        
        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp
        
        amount_recovered =  new_hp_value - self.hp
        
        self.hp = new_hp_value
        return amount_recovered
    
    def take_damage(self, amount: int) -> None:
        self.hp -= amount
