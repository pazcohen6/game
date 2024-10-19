from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction
from entity import Actor

if TYPE_CHECKING:
    from entity import Actor

"""
BaseAI class:
    An abstract class that provides basic AI functionality for entities.
    Inherits from both Action and BaseComponent, enabling AI-controlled actions
    and interaction with the game's component system.

Methods:
    perform:
        An abstract method meant to be overridden by subclasses to define
        specific AI behavior.
    
    get_path_to:
        Computes and returns a path to a target position using a pathfinding
        algorithm. The path avoids obstacles and accounts for other entities
        blocking movement.

        Input:
            > dest_x (int): The x-coordinate of the target position.
            > dest_y (int): The y-coordinate of the target position.

        Return:
            > List[Tuple[int, int]]: A list of (x, y) tuples representing the path
              to the target position. Returns an empty list if no valid path is found.
"""
class BaseAI(Action):
    entity: Action

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]

"""
HostileEnemy class:
    A subclass of BaseAI representing an enemy AI that will actively seek out
    and attack the player. The enemy will move towards the player if not in
    melee range, or attack if close enough.

Methods:
    __init__:
        Initializes the HostileEnemy with the given entity and sets up an
        empty path list for movement.

        Input:
            > entity (Actor): The entity controlled by this AI.
    
    perform:
        Executes the AI's decision-making process each turn. If the player is
        visible, the enemy will either move towards the player or attack if
        within melee range. If no valid move is available, the enemy will wait.

        Return:
            > None
"""
class HostileEnemy(BaseAI):
   def __init__(self, entity: Actor):
       super().__init__(entity)
       self.path: List[Tuple[int, int]] = []

   def perform(self) -> None:
       target = self.engine.player
       dx = target.x - self.entity.x
       dy = target.y - self.entity.y
       distance = max(abs(dx), abs(dy))  # Chebyshev distance.

       if self.engine.game_map.visible[self.entity.x, self.entity.y]:
           if distance <= 1:
               return MeleeAction(self.entity, dx, dy).perform()
           
           self.path = self.get_path_to(target.x, target.y)

       if self.path:
           dest_x, dest_y = self.path.pop(0)
           return MovementAction(
               self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
           ).perform()
       
       return WaitAction(self.entity).perform()

"""
ConfusedEnemy class:
    A subclass of BaseAI that represents an enemy temporarily confused, moving
    randomly for a certain number of turns before reverting to its original AI.

Methods:
    __init__:
        Initializes the ConfusedEnemy with the entity, its previous AI, and
        the number of turns it remains confused.

        Input:
            > entity (Actor): The entity controlled by this AI.
            > previous_ai (Optional[BaseAI]): The original AI to revert to.
            > turns_remaining (int): The number of turns the entity remains confused.
    
    perform:
        Executes the AI's behavior while confused. The entity will move randomly
        each turn, attacking if it bumps into another actor. After the effect
        expires, the entity reverts to its original AI.

        Return:
            > None
"""
class ConfusedEnemy(BaseAI):
    def __init__(
            self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
        ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f'The {self.entity.name} in no longer confused.'
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )
            self.turns_remaining -= 1
            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.            
            return BumpAction(self.entity, direction_x, direction_y,).perform()