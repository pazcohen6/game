from __future__ import annotations
from typing import TYPE_CHECKING

from entity import Entity

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


# Define a base class for all actions
# TODO
class Action:
    def preform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()

# Define a subclass for escape action.
# TODO
class EscapeAction(Action):
    def preform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()

# Define a subclass for movement action, with includes info about movement direction
class MovementAction(Action):
    """ Constracter for MovementAction
            > dx : movement in x direction
            > dx : movement in y direction
     """
    def __init__ (self,dx : int,dy : int):
        super().__init__()

        self.dx = dx
        self.dy = dy

    """ Preform an Action if possible
            > engien : the game engne to preform on
            > entity : the entity the that preform the action
    """
    def preform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if not engine.game_map.in_bounds(dest_x, dest_y):
            return # Destination is out of bounds.
        if not engine.game_map.tiles['walkable'][dest_x, dest_y]:
            return # Destination is blocked by a wall taile.
        
        entity.move(self.dx, self.dy)