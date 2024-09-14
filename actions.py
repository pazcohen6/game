from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

import color
from entity import Actor
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


"""
Action class:
    A base class for all actions that can be performed by entities in the game.
    Actions represent different behaviors or interactions, such as moving, attacking,
    or waiting.

Attributes:
    entity (Actor):
        The entity that performs the action.

Methods:
    engine (property):
        Returns the game engine associated with the entity performing the action.
        This allows actions to interact with the game world.

        Return:
            > Engine: The game engine this action belongs to.

    perform:
        Executes the action. This method must be overridden by subclasses to define
        specific behaviors for different actions.

        Raise:
            > NotImplementedError: If the method is not overridden in a subclass.
"""
class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity
    
    @property
    def engine(self) -> Engine:
        """Return the engien this action belong to."""
        return self.entity.gamemap.engine
    
    def perform(self) -> None:
        """perform this action with the objects needed to determine its scope.
        `self.engine` is the scope this action is being performed in.
        `self.entity` is the object performing the action.
        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()

#TODO
class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""
    def __init__(self, entity: Actor) -> None:
        super().__init__(entity)
    
    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")
                
                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f'You picked up the {item.name}!')
                return
        raise exceptions.Impossible("There is nothing to pick up")
    
#TODO
class ItemAction(Action):
    def __init__(
            self, entity:Actor, item: Item, target_xy: Optional[Tuple[int,int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy
    
    @property
    def target_actor(self) -> Optional[Action]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        self.item.consumable.activate(self)

"""
    TODO
"""
class DropItem(ItemAction):
    def perform(self) -> None:
        self.entity.inventory.drop(self.item)
    
"""
WaitAction class (inherits from Action):
    An action that causes the entity to do nothing for a turn.

Methods:
    perform:
        Performs no operation, effectively causing the entity to wait.
"""
class WaitAction(Action):
    def perform(self) -> None:
        pass

"""
    TODO Take the stairs, if any exist at the entity's location.
"""
class TakeStairsAction(Action):
    def perform(self) -> None:
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")
"""
ActionWithDirection class (inherits from Action):
    A base class for actions that require a direction, such as movement or attacking.
    This class provides properties to determine the destination coordinates and
    to check for entities at the destination.

Attributes:
    dx (int):
        The change in the x-coordinate for the action.
    dy (int):
        The change in the y-coordinate for the action.

Methods:
    dest_xy (property):
        Calculates and returns the destination coordinates based on the entity's
        current position and the direction of the action.

        Return:
            > Tuple[int, int]: The (x, y) coordinates of the destination.

    blocking_entity (property):
        Checks if there is a blocking entity at the destination.

        Return:
            > None: Currently does not return an entity, but checks for blocking.

    target_actor (property):
        Checks if there is an actor (entity) at the destination.

        Return:
            > Optional[Actor]: The actor at the destination, if any.
"""
class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)
        
        self.dx = dx
        self.dy = dy
    
    @property
    def dest_xy(self) -> Tuple[int,int]:
        return self.entity.x + self.dx, self.entity.y + self.dy
    
    @property
    def blocking_entity(self) -> None:
        return self.engine.game_map.get_blocking_ntity_at_location(*self.dest_xy)
    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)
    def perform(self) -> None:
        raise NotImplementedError()

"""
MeleeAction class (inherits from ActionWithDirection):
    An action that causes the entity to perform a melee attack on a target actor.

Methods:
    perform:
        Executes the melee attack. If a target is present, calculates the damage
        based on the entity's power and the target's defense. Logs the attack
        message and applies damage if any.

        Return:
            > None
"""
class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack")
        
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk
        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f'{attack_desc} but does no damage', attack_color
            )

"""
MovementAction class (inherits from ActionWithDirection):
    An action that moves the entity to a new position if the destination is valid.

Methods:
    perform:
        Moves the entity in the specified direction if the destination is within
        bounds, walkable, and not blocked by another entity.

        Return:
            > None
"""
class MovementAction(ActionWithDirection):

    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy
         

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles['walkable'][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_ntity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("That way is blocked.")
        self.entity.move(self.dx, self.dy)

"""
BumpAction class (inherits from ActionWithDirection):
    An action that performs either a melee attack or a movement, depending on
    whether there is a target actor at the destination.

Methods:
    perform:
        Checks for a target actor at the destination. If found, performs a melee
        attack. Otherwise, performs a movement action.

        Return:
            > None
"""
class BumpAction(ActionWithDirection):
    def perform(self) -> None:

        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        
        else:
            return MovementAction(self.entity ,self.dx, self.dy).perform()
                
