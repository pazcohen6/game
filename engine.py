from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console

from entity import Entity
from input_handlers import EventHandler
from game_map import GameMap

class Engine:
    """
        constractor for the class.
            > entities - set of entities.
            > event_handler - handel the events.
            > player - player entity for better access.
    """
    def __init__(self, entities: Set[Entity], event_handler: EventHandler, game_map: GameMap, player: Entity):
        self.entities = entities
        self.event_handler = event_handler
        self.player = player
        self.game_map = game_map

    """
        handle the event and update the relevant 
            > events : the events to execut
    """
    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.preform(self, self.player)
    """
        iterate through the entities and draw on the screan
            > console :  the console to clear
            > context : the context to present
    """        
    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        for entity in self.entities:
            console.print(entity.x, entity.y, entity.char, fg=entity.color)

        context.present(console)

        console.clear()