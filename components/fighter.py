from __future__ import annotations

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent
from input_handlers import GameOverEventHandler
from render_order import RendrOrder

if TYPE_CHECKING:
    from entity import Actor
"""
Fighter class:
    A component that adds combat-related attributes and behavior to an entity,
    such as health points (HP), defense, and power. It also handles damage,
    death, and interactions related to combat.

Attributes:
    entity (Actor):
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
"""
class Fighter(BaseComponent):
    entity: Actor

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

        if self._hp == 0 and self.entity.ai:
            self.die()

    def die(self) -> None:
        if self.engine.player is self.entity:
            death_massage = "You Died"
            death_massage_color = color.player_die
            self.engine.event_handler = GameOverEventHandler(self.engine)

        else:
            death_massage = f"you've defeated {self.entity.name}"
            death_massage_color = color.enemy_die

        self.entity.char = "%"
        self.entity.color = (191,0,0)
        self.entity.blocks_movement = False
        self.entity.ai = None
        self.entity.name = f"remains of {self.entity.name}"
        self.entity.render_order = RendrOrder.CORPSE

        self.engine.message_log.add_messge(death_massage, death_massage_color)