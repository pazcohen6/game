from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import tcod.event
from actions import Action, BumpAction, EscapeAction, WaitAction

if TYPE_CHECKING:
    from engine import Engine

MOVE_KEYS = {
    # Numpad keys :
    tcod.event.K_KP_1 : (-1,1),
    tcod.event.K_KP_2 : (0,1),
    tcod.event.K_KP_3 : (1,1),
    tcod.event.K_KP_4 : (-1,0),
    tcod.event.K_KP_6 : (1,0),
    tcod.event.K_KP_7 : (-1,-1),
    tcod.event.K_KP_8 : (0,-1),
    tcod.event.K_KP_9 : (1,-1),
    # wad
    tcod.event.K_z : (-1,1),
    tcod.event.K_x : (0,1),
    tcod.event.K_c : (1,1),
    tcod.event.K_a : (-1,0),
    tcod.event.K_d : (1,0),
    tcod.event.K_q : (-1,-1),
    tcod.event.K_w : (0,-1),
    tcod.event.K_e : (1,-1),
}

WAIT_KEYS = {
    tcod.event.K_s,
    tcod.event.K_KP_5,
}
# EventHandler class that processes game events and dispatches corresponding actions.
# Subclass of tcod's EevntDispatch
# TODO
class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def handle_events(self) -> None:
        raise SystemExit()

    # Handle the quit event by raising SystemExit to exit the game.
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()


class MainGameEventHandler(EventHandler):
    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue
        
            action.perform()

            self.engine.handle_enemy_turns()
            self.engine.update_fov() # Update the FOV before the players next action.

    # Handle keydown events and map them to corresponding actions.
    # The method receive a key press event and return an Action subclass or None
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        
        action : Optional[Action] = None

        # get the pressed key form the system
        key = event.sym

        player = self.engine.player

        # actions to move up, down, left and right.
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        
        # action to wait and do mothing
        elif key in WAIT_KEYS:
            action = WaitAction(player)

        # action esc to Quit the game
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        return action
    
class GameOverEventHandler(EventHandler):
    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym
        
        if key == tcod.event.K_ESCAPE:
            action = EscapeAction(self.engine.player)

        # no valid key was pressed
        return action