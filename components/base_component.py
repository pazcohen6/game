from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

"""
BaseComponent class:
    A base class for components that can be attached to entities in the game.
    Components add functionality or data to entities and can interact with the
    game engine.

Attributes:
    entity (Entity):
        The entity instance that owns this component.

Methods:
    engine:
        A property that returns the game engine associated with this component's entity.
        This allows components to interact with the broader game environment.

        Return:
            > Engine: The game engine associated with the owning entity.
"""
class BaseComponent:
    entity: Entity  # Owning entity instance.

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine