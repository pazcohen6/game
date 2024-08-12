
from __future__ import annotations
import copy
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING

from render_order import RendrOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
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

Methods:
    __init__:
        Initializes a new entity with the given attributes and optionally associates it with
        a game map.

        Parameters:
            gamemap (Optional[GameMap]): The game map instance.
            x (int): The x-coordinate position.
            y (int): The y-coordinate position.
            char (str): The character symbol.
            color (Tuple[int, int, int]): The RGB color.
            name (str): The name of the entity.
            blocks_movement (bool): Whether the entity blocks movement.
            render_order (RendrOrder): The rendering order of the entity.

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
            y (int): The new y-coordinate position.
            gamemap (Optional[GameMap]): The new game map instance.

    move:
        Updates the position of the entity based on the provided movement offsets.

        Parameters:
            dx (int): The movement offset in the x direction.
            dy (int): The movement offset in the y direction.
"""
class Entity :

    gamemap : GameMap

    def __init__ (
            self,
            gamemap: Optional[GameMap] = None,
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

        if gamemap:
            # If gamemap isn't provided now then it will be set later.
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def spawn(self:T, gamemap:GameMap, x:int, y:int) -> T:
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add(clone)
        return clone
    
    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "gamemap"): # Possibly uninitialized.
                self.gamemap.engine.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)

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
            fighter (Fighter): The combat statistics of the actor.

    is_alive:
        Returns whether the actor is alive based on the presence of AI.

        Returns:
            bool: True if the actor has AI and is thus considered alive.
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
       fighter: Fighter
   ):
       super().__init__(
           x=x,
           y=y,
           char=char,
           color=color,
           name=name,
           blocks_movement=True,
           render_order= RendrOrder.ACTOR
       )
       self.ai: Optional[BaseAI] = ai_cls(self)
       self.fighter = fighter
       self.fighter.entity = self
   @property
   def is_alive(self) -> bool:
       """Returns True as long as this actor can perform actions."""
       return bool(self.ai)