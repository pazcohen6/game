from __future__ import annotations

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent
from render_order import RendrOrder

if TYPE_CHECKING:
    from entity import Actor
    
"""
Fighter class:
    A component that adds combat-related attributes and behavior to an entity,
    such as health points (HP), defense, and power. It also handles damage,
    death, and interactions related to combat.

Attributes:
    parent (Actor):
        The entity instance that owns this component.
    max_hp (int):
        The maximum health points for the entity.
    _hp (int):
        The current health points for the entity.
    defense (int):
        The defense value that reduces incoming damage.
    power (int):
        The attack power of the entity.

Methods:
    hp (property):
        A getter and setter for the entity's current health points.
        The setter ensures that HP does not exceed max_hp and triggers death
        if HP reaches zero.

        Return:
            > int: The current health points of the entity.

    die:
        Handles the death of the entity. Updates the entity's state to represent
        a dead body, logs a death message, and switches the player to the game
        over event handler if the player dies.

        Return:
            > None

    heal:
        Restores health points to the entity, up to the maximum HP. Returns the
        amount of health recovered.

        Input:
            > amount (int): The amount of health to restore.

        Return:
            > int: The amount of HP recovered.

    take_damage:
        Reduces the entity's current health points by the given amount and checks
        if the entity should die.

        Input:
            > amount (int): The amount of damage taken.

        Return:
            > None
"""
class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))

        if self._hp == 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_massage = "You Died"
            death_massage_color = color.player_die
        else:
            death_massage = f"you've defeated {self.parent.name}"
            death_massage_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191,0,0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RendrOrder.CORPSE

        self.engine.message_log.add_message(death_massage, death_massage_color)

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
