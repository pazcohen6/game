from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item

"""
Inventory class:
    A component that manages an entity's inventory, allowing it to store and
    drop items.

Attributes:
    parent (Actor):
        The entity instance that owns this component.
    capacity (int):
        The maximum number of items the inventory can hold.
    items (List[Item]):
        A list of items currently in the inventory.

Methods:
    drop:
        Removes an item from the inventory and places it at the entity's current
        location on the game map.

        Input:
            > item (Item): The item to be dropped.

        Return:
            > None
"""
class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, 
        at the player's current location.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f'You dropped the {item.name}.')
        