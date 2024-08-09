from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

import color

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity


# Define a base class for all actions
# TODO
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

# Define a subclass for escape action.
# TODO
class EscapeAction(Action):
    def perform(selfy) -> None:
        raise SystemExit()
    
# TODO
class WaitAction(Action):
    def perform(self) -> None:
        pass

# TODO
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

# TODO
class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            return # No entity to attack.
        
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk
        if damage > 0:
            self.engine.message_log.add_messge(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_messge(
                f'{attack_desc} but does no damage', attack_color
            )

# Define a subclass for movement action, with includes info about movement direction
# TODO
class MovementAction(ActionWithDirection):

    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy
         

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return # Destination is out of bounds.
        if not self.engine.game_map.tiles['walkable'][dest_x, dest_y]:
            return # Destination is blocked by a wall taile.
        if self.engine.game_map.get_blocking_ntity_at_location(dest_x, dest_y):
            return # Destination is block by an entity.
        self.entity.move(self.dx, self.dy)

# TODO
class BumpAction(ActionWithDirection):
    def perform(self) -> None:

        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        
        else:
            return MovementAction(self.entity ,self.dx, self.dy).perform()
                
