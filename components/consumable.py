from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.ai
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler, 
    SingleRangedAttackHandler)

if TYPE_CHECKING:
    from entity import Actor, Item

"""
Consumable class:
    A base class for items that can be consumed by an actor. Consumables typically
    provide some effect or ability when used.

Attributes:
    parent (Item):
        The item instance that owns this component.

Methods:
    get_action:
        Attempts to return the action that will be performed by the consumer when this
        item is used.

        Input:
            > consumer (Actor): The actor consuming the item.

        Return:
            > Optional[ActionOrHandler]: The action to be performed.
    
    activate:
        Triggers the item's ability.

        Input:
            > action (ItemAction): The context in which the item is activated.
        
        Return:
            > None

    consume:
        Removes the consumed item from the inventory it is in.

        Return:
            > None
"""
class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)
    
    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this items ability.
           'action' is the context for this activation """
        raise NotImplementedError()
    
    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)

"""
ConfusionConsumable class:
    A subclass of Consumable that applies a confusion effect to a target, causing them
    to move randomly for a set number of turns.

Attributes:
    number_of_turns (int):
        The duration of the confusion effect in turns.

Methods:
    get_action:
        Returns the action to target a location for the confusion effect.

        Input:
            > consumer (Actor): The actor consuming the item.

        Return:
            > SingleRangedAttackHandler: A handler to select the target location.
    
    activate:
        Activates the confusion effect on the selected target.

        Input:
            > action (ItemAction): The context for the item's activation.
        
        Return:
            > None
"""
class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback= lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )
    
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself.")
        
        self.engine.message_log.add_message(
            f'The eyes of the {target.name} look vacant, as it starts to stumble around!',
            color.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity = target, previous_ai = target.ai, turns_remaining = self.number_of_turns,
        )
        self.consume()

"""
HealingConsumable class:
    A subclass of Consumable that heals the consumer by a specified amount.

Attributes:
    amount (int):
        The amount of health to be restored.

Methods:
    activate:
        Activates the healing effect on the consumer.

        Input:
            > action (ItemAction): The context for the item's activation.
        
        Return:
            > None
"""
class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP",
                color.health_recoverd,
            )
            self.consume()
        else:
            raise Impossible(f'Your health is already full.')
        
"""
LightningDamageConsumable class:
    A subclass of Consumable that strikes the closest visible enemy with lightning,
    dealing a specified amount of damage.

Attributes:
    damage (int):
        The amount of damage dealt by the lightning strike.
    
    maximum_range (int):
        The maximum range at which the lightning can strike.

Methods:
    activate:
        Activates the lightning strike on the closest enemy within range.

        Input:
            > action (ItemAction): The context for the item's activation.
        
        Return:
            > None
"""
class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance
        
        if target:
            self.engine.message_log.add_message(
                f'A lightning bolt strike the {target.name} with  loud thunder, for {self.damage} damage!'
            )
            
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")
        
"""
FirecubeDamageConsumable class:
    A subclass of Consumable that creates an explosion in a selected area, dealing
    damage to enemies within a specified radius.

Attributes:
    damage (int):
        The amount of damage dealt by the explosion.
    
    radius (int):
        The radius of the explosion.

Methods:
    get_action:
        Returns the action to target a location for the fire explosion.

        Input:
            > consumer (Actor): The actor consuming the item.

        Return:
            > AreaRangedAttackHandler: A handler to select the target area.
    
    activate:
        Activates the fire explosion at the selected target location.

        Input:
            > action (ItemAction): The context for the item's activation.
        
        Return:
            > None
"""
class FirecubeDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius = self.radius,
            callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see")
        
        targets_hit = False
        for actor in self.engine.game_map.actors:

            if actor.distance(*target_xy) < self.radius:
                self.engine.message_log.add_message(
                    f'The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!'
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no enemys in the radius.")
        self.consume()
