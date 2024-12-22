from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from game_map import GameMap

"""
BaseComponent class:
    A base class for components that can be attached to entities in the game.
    Components add functionality or data to entities and can interact with the
    game engine.

Attributes:
    patent (Entity):
        The entity instance that owns this component.

Methods:
    gamemap:
        A property that returns the game map associated with the component's entity.

        Return:
            > GameMap: The game map the entity is located in.
    
    engine:
        A property that returns the game engine associated with this component's entity.
        This allows components to interact with the broader game environment.

        Return:
            > Engine: The game engine associated with the owning entity.
"""
class BaseComponent:
    parent: Entity  # Owning entity instance.

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    @property
    def engine(self) -> Engine:
        return self.gamemap.engine