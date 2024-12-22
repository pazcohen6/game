from __future__ import annotations
import copy
import math
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

#from game_map import GameMap
from render_order import RendrOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.equipment import Equipment
    from components.equippable import Equippable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.level import Level
    from game_map import GameMap

T = TypeVar("T", bound="Entity")

"""
Entity class:
    Represents a general entity in the game world. Other classes such as "Player",
    "NPC", and "Enemy" will inherit from this class.

Attributes:
    gamemap (GameMap):
        The game map instance where the entity is located. It will be set when the entity
        is placed or spawned in the game world.
    x (int):
        The x-coordinate position of the entity on the game map.
    y (int):
        The y-coordinate position of the entity on the game map.
    char (str):
        The character symbol representing the entity.
    color (Tuple[int, int, int]):
        The RGB color value of the entity.
    name (str):
        The name of the entity.
    blocks_movement (bool):
        Indicates whether the entity blocks movement on the map.
    render_order (RendrOrder):
        The rendering order of the entity, which determines the drawing order on the map.
    level (Level):
        The level component for the entity, which tracks the entity's level, experience, and progression.

Methods:
    __init__:
        Initializes a new entity with the given attributes and optionally associates it with
        a game map.

        Parameters:
            parent (Optional[GameMap]): The game map instance.
            x (int): The x-coordinate position.
            y (int): The y-coordinate position.
            char (str): The character symbol.
            color (Tuple[int, int, int]): The RGB color.
            name (str): The name of the entity.
            blocks_movement (bool): Whether the entity blocks movement.
            render_order (RendrOrder): The rendering order of the entity.
    
    gamemap (property):
        Retrieves the game map instance the entity is associated with.
        
        Returns:
            GameMap: The game map where the entity is located.

    spawn:
        Creates a clone of the entity and places it at a new position on a new game map.

        Parameters:
            gamemap (GameMap): The new game map instance.
            x (int): The new x-coordinate position.
            y (int): The new y-coordinate position.

        Returns:
            T: The cloned entity.

    place:
        Moves the entity to a new position on the specified game map. Updates the game map
        associations as necessary.

        Parameters:
            x (int): The new x-coordinate position.
            y (int): The new game map instance.
            gamemap (Optional[GameMap]): The new game map instance.

    distance:
        Calculates the distance between the current entity and the provided (x, y) coordinates.

        Parameters:
            x (int): The x-coordinate of the target position.
            y (int): The y-coordinate of the target position.

        Returns:
            float: The calculated distance.

    move:
        Updates the entity's position based on movement offsets.

        Parameters:
            dx (int): The movement offset in the x direction.
            dy (int): The movement offset in the y direction.
"""
class Entity :

    parent : Union[GameMap, Inventory]

    def __init__ (
            self,
            parent: Optional[GameMap] = None,
            x:int =0,
            y:int =0,
            char: str = "?",
            color: Tuple[int, int, int] = (255, 255, 255),
            name: str = "<Unnamed>",
            blocks_movement: bool = False,
            render_order: RendrOrder = RendrOrder.CORPSE
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order

        if parent:
            # If gamemap isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap
    
    def spawn(self:T, gamemap:GameMap, x:int, y:int) -> T:
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone
    
    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"): # Possibly uninitialized.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """Return the distance between the current entity and the given (x, y) coordinate."""
        return max(abs(x -self.x) , abs(y-self.y))

    def move(self, dx:int, dy:int) -> None:
        self.x += dx
        self.y += dy

"""
Actor class:
    Represents an entity with additional attributes for AI and combat. This class
    extends the base Entity class to include attributes specific to actors, such as
    AI behavior and combat stats.

Attributes:
    ai (Optional[BaseAI]):
        The AI instance controlling the actor's behavior. It is initialized using the
        provided AI class.
    fighter (Fighter):
        The combat statistics of the actor, including health, defense, and power.
    inventory (Inventory):
        The inventory of the actor, containing items the actor can carry.
    level (Level):
        The level component of the actor, which tracks experience, level-ups, and stat progression.
    equipment (Equipment):
        The equipment component of the actor, which handles equippable items like weapons and armor.

Methods:
    __init__:
        Initializes a new actor with the specified attributes and AI behavior.

        Parameters:
            x (int): The x-coordinate position.
            y (int): The y-coordinate position.
            char (str): The character symbol.
            color (Tuple[int, int, int]): The RGB color.
            name (str): The name of the actor.
            ai_cls (Type[BaseAI]): The AI class for the actor.
            equipment (Equipment): The equipment component of the actor.
            fighter (Fighter): The combat statistics of the actor.
            inventory (Inventory): The actor's inventory.
            level (Level): The level component of the actor.

    is_alive (property):
        Checks if the actor is alive based on whether it has AI.

        Returns:
            bool: True if the actor has AI and is considered alive, otherwise False.
"""
class Actor(Entity):
    def __init__(
       self,
       *,
       x: int = 0,
       y: int = 0,
       char: str = "?",
       color: Tuple[int, int, int] = (255, 255, 255),
       name: str = "<Unnamed>",
       ai_cls: Type[BaseAI],
       equipment: Equipment,
       fighter: Fighter,
       inventory: Inventory,
       level: Level,
    ):
        super().__init__(
           x=x,
           y=y,
           char=char,
           color=color,
           name=name,
           blocks_movement=True,
           render_order= RendrOrder.ACTOR,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.equipment: Equipment = equipment
        self.equipment.parent = self
       
        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.level = level
        self.level.parent = self
       
    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

"""
Item class:
    Represents an item that can be picked up and used in the game. Inherits from the
    Entity class and includes additional functionality for consumables and equippables.

Attributes:
    consumable (Optional[Consumable]):
        The consumable component, defining the item's effect when used.
    equippable (Optional[Equippable]):
        The equippable component, defining the item's effect when equipped.

Methods:
    __init__:
        Initializes an item with position, symbol, color, name, and optional 
        consumable and equippable components.

        Parameters:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            char (str): The character symbol representing the item.
            color (Tuple[int, int, int]): The item's RGB color.
            name (str): The name of the item.
            consumable (Optional[Consumable]): The consumable component of the item.
            equippable (Optional[Equippable]): The equippable component of the item.
"""
class Item(Entity):
    def __init__(
            self,
            *, 
            x: int = 0, 
            y: int = 0, 
            char: str = "?", 
            color: Tuple[int] = (255, 255, 255), 
            name: str = "<Unnamed>", 
            consumable: Optional[Consumable] = None,
            equippable: Optional[Equippable] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RendrOrder.ITEM,
        )

        self.consumable = consumable
        
        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self