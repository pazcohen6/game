from __future__ import annotations

import os

from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union
import tcod
from tcod.console import Console
import tcod.event

import actions
from actions import (Action, 
                     BumpAction, 
                     PickupAction,
                     WaitAction,
                     )

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

# Dictionary mapping keys to movement directions
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
    # wasd
#    tcod.event.K_z : (-1,1),
#    tcod.event.K_x : (0,1),
#    tcod.event.K_c : (1,1),
#    tcod.event.K_a : (-1,0),
#    tcod.event.K_d : (1,0),
#    tcod.event.K_q : (-1,-1),
#    tcod.event.K_w : (0,-1),
#    tcod.event.K_e : (1,-1),
}

# Set of keys used for waiting or pausing actions
WAIT_KEYS = {
    tcod.event.K_s,
    tcod.event.K_KP_5,

# Constants for confirming actions:
# This set contains key events that can be used to confirm actions in the game.
}
CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}

# Dictionary mapping cursor keys to movement values
CURSOR_Y_KEY = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: 10,
    tcod.event.K_PAGEDOWN: -10,

}

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""
BaseEventHandler class:
    A base class for handling events in the game. It processes incoming events and can
    switch between active event handlers or trigger actions based on the event type.

Attributes:
    None

Methods:
    handle_events:
        Processes an event and returns the next active event handler.
        Parameters:
            event (tcod.event.Event): The event to be handled.
        Return:
            > BaseEventHandler: The next active event handler.

    on_render:
        Renders the current state of the game.
        Parameters:
            console (tcod.console.Console): The console where the game state is rendered.
        Return:
            > None

    ev_quit:
        Handles the quit event by raising a SystemExit exception.
        Parameters:
            event (tcod.event.Quit): The quit event.
        Return:
            > None
"""
class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f'{self!r} can not handle aactions'
        return self
    
    def on_render(self, console: tcod.console) -> None:
        raise NotImplementedError()
    
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

"""
PopupMessage class:
    Displays a popup message on the screen while retaining the parent handler's state.

Attributes:
    parent (BaseEventHandler):
        The parent event handler that will be rendered in the background.
    text (str):
        The message to display in the popup.

Methods:
    on_render:
        Renders the parent handler and then displays the popup message.
        Parameters:
            console (tcod.console.Console): The console to render the popup and parent state.
        Return:
            > None

    ev_keydown:
        Handles keydown events, and closes the popup by returning to the parent handler.
        Parameters:
            event (tcod.event.KeyDown): The keydown event.
        Return:
            > BaseEventHandler: The parent handler, closing the popup.
"""
class PopupMessage(BaseEventHandler):
    def __init__(self, parant_hndler: BaseEventHandler, text: str):
        self.parant = parant_hndler
        self.text = text

    def on_render(self, console: tcod.console.Console) -> None:
        self.parant.on_render(console)
        console.print(
            console.width // 2,
            console.height // 2 - 8,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        return self.parant
"""
EventHandler class:
    Processes game events and dispatches corresponding actions. It extends the BaseEventHandler
    to handle game-specific event logic and interactions with the game engine.

Attributes:
    engine (Engine):
        The engine instance that manages the game state, entities, and logic.

Methods:
    handle_events:
        Processes an event and either switches to a different event handler or processes
        actions that affect the game state.
        Parameters:
            event (tcod.event.Event): The event to be handled.
        Return:
            > BaseEventHandler: The next active event handler.

    handle_action:
        Processes an action and checks if it is valid, performing it if so.
        If an action is performed, it updates the game state.
        Parameters:
            action (Optional[Action]): The action to handle.
        Return:
            > bool: True if the action advances the game turn, False otherwise.

    ev_mousemotion:
        Updates the engine's mouse location based on mouse movement events.
        Parameters:
            event (tcod.event.MouseMotion): The mouse motion event.
        Return:
            > None

    on_render:
        Renders the current game state to the provided console.
        Parameters:
            console (tcod.console.Console): The console to render the game state.
        Return:
            > None
"""
class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.
        Returns True if the action will advance a turn."""
        if action is None:
            return False
       
        try:
            action.perform()
        except exceptions.Impossible as exc:
           self.engine.message_log.add_message(exc.args[0], color.impossible)
           return False # Skip enemy turn on excpetion.
        
        self.engine.handle_enemy_turns()
       
        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.context.Context) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)

"""
MainGameEventHandler class:
    Handles events during the main game loop, processes player actions, and manages
    game-specific interactions. It extends the EventHandler class.

Methods:
    ev_keydown:
        Handles keydown events, maps them to corresponding actions, and triggers
        appropriate handlers or actions based on the key pressed.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[ActionOrHandler]: The action or handler triggered by the key press,
              or None if no action is triggered.
"""
class MainGameEventHandler(EventHandler):
    # Handle keydown events and map them to corresponding actions.
    # The method receive a key press event and return an Action subclass or None
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        
        action : Optional[Action] = None

        # get the pressed key form the system
        key = event.sym
        modifier = event.mod
        player = self.engine.player

        if key == tcod.event.K_EQUALS or key == tcod.event.K_u:
            return actions.TakeStairsAction(player)
        
        # actions to move up, down, left and right.
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        
        # action to wait and do mothing
        elif key in WAIT_KEYS:
            action = WaitAction(player)

        # action esc to Quit the game
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        
        elif key == tcod.event.K_v:
            return HistoryViewer(self.engine)

        elif key == tcod.event.K_g:
            action = PickupAction(player)

        elif key == tcod.event.K_i:
            return InventoryActivateHndler(self.engine)
        elif key == tcod.event.K_d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.K_c:
            return CaracterScreenEventHandler(self.engine)
        elif key == tcod.event.K_SLASH or key == tcod.event.K_KP_DIVIDE:
            return LookHandler(self.engine)

        
        # No valid key was predded
        return action

"""
GameOverEventHandler class:
    Handles events when the game is over, including clean-up operations and exiting
    the game. It extends the EventHandler class.

Methods:
    on_quit:
        Handles the cleanup and exit process when the game is finished. It removes
        any existing save game files and raises an exception to quit the game without saving.

        Return:
            > None

    ev_quit:
        Handles the quit event, triggering the on_quit method to perform cleanup and exit.

        Parameters:
            event (tcod.event.Quit): The quit event.

        Return:
            > None

    ev_keydown:
        Handles keydown events and performs the exit action if the escape key is pressed.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[Action]: Returns None if the escape key is pressed, triggering the on_quit method.
"""   
class GameOverEventHandler(EventHandler): 
    def on_quit(self) -> None:
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")
        raise exceptions.QuitWithoutSaveing()
    
    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit

"""
HistoryViewer class:
    Displays and allows navigation of the message history in a larger, custom window.
    It inherits from EventHandler and provides functionality for viewing and navigating
    through the game's message log.

Attributes:
    log_length (int):
        The total number of messages in the message log.
    cursor (int):
        The current position of the cursor within the message log.

Methods:
    on_render:
        Renders the message history on a custom console, including a frame and a title.

        Parameters:
            console (tcod.console.Console): The console to which the message history is rendered.

        Return:
            > None

    ev_keydown:
        Handles keydown events to navigate through the message history. Moves the cursor based on
        specific keys and returns to the main game state if another key is pressed.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[MainGameEventHandler]: Returns the MainGameEventHandler if a navigation key
              is pressed; otherwise, returns None.
"""
class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_leangth = len(engine.message_log.messages)
        self.cursor = self.log_leangth - 1

    def on_render(self, console: Console) -> None:
        super().on_render(console) # Draw the main state as the background.

        log_console = tcod.console.Console(console.width - 6, console.height - 6)
        
        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤ Message History ├", alignment=tcod.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2 ,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEY:
            adjust = CURSOR_Y_KEY[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_leangth - 1
            elif adjust > 0 and self.cursor == self.log_leangth -1 :
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_leangth - 1))
        
        elif event.sym == tcod.event.K_HOME :
            self.cursor = 0 # Move directly to the top message.
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_leangth - 1 # Move directly to the last message.
        else :  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None

"""
AskUserEventHandler class:
    Handles user input for actions requiring special input or confirmation. It provides
    default behavior to exit the input handler on any key press or mouse click.

Methods:
    ev_keydown:
        Handles keydown events and exits the input handler for any non-modifier key.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[ActionOrHandler]: Returns the result of on_exit() method.

    ev_mousebuttondown:
        Handles mouse button down events and exits the input handler.

        Parameters:
            event (tcod.event.MouseButtonDown): The mouse button down event.

        Return:
            > Optional[ActionOrHandler]: Returns the result of on_exit() method.

    on_exit:
        Handles the exit or cancellation of an action and returns to the main event handler.

        Return:
            > Optional[ActionOrHandler]: Returns the MainGameEventHandler instance.
"""
class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in { # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()
    
    def ev_mousebuttondown(
            self, event: tcod.event.MouseButtonDown
        ) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()
    
    def on_exit(self) -> Optional[ActionOrHandler]:
        """
        Called when the user is trying to exit or cancel an action.
        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)
"""
CaracterScreenEventHandler class:
    Displays detailed information about the player's character in a separate screen.
    Inherits from AskUserEventHandler.

Attributes:
    TITLE (str):
        The title displayed at the top of the character information window.

Methods:
    on_render:
        Renders the character information to the console, including level, XP, attack, and defense stats.

        Parameters:
            console (Console): The console to render the character information.

        Return:
            > None
"""
class CaracterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"
    def on_render(self, console: Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x = x,
            y = y,
            width = width,
            height = 7,
            title = self.TITLE,
            clear = True,
            fg = (255, 255, 255),
            bg = (0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}"
        )
        console.print(
            x=x + 1, y=y + 2, string=f"XP: {self.engine.player.level.current_xp}"
        )
        console.print(
            x=x + 1,
            y=y + 3,
            string=f"XP for next Level: {self.engine.player.level.experience_to_next_level}",
        )
        console.print(
            x=x + 1, y=y + 4, string=f"Attack: {self.engine.player.fighter.power}"
        )
        console.print(
            x=x + 1, y=y + 5, string=f"Defense: {self.engine.player.fighter.defense}"
        )

"""
LevelUpEventHandler class:
    Handles events when the player levels up, allowing the user to select an attribute to increase.
    Inherits from AskUserEventHandler.

Attributes:
    TITLE (str):
        The title displayed at the top of the level-up window.

Methods:
    on_render:
        Renders the level-up interface and options to the console.

        Parameters:
            console (Console): The console to render the level-up interface.

        Return:
            > None

    ev_keydown:
        Handles keydown events to select an attribute to increase.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[ActionOrHandler]: Returns the result of on_exit() or action based on selected attribute.

    ev_mousebuttondown:
        Prevents mouse clicks from exiting the menu.

        Parameters:
            event (tcod.event.MouseButtonDown): The mouse button down event.

        Return:
            > Optional[ActionOrHandler]: Always returns None to prevent exit.
"""
class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up"

    def on_render(self, console: Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30 :
            x = 40
        else :
            x = 0
        
        console.draw_frame(
            x = x,
            y = 0,
            width = 35,
            height = 8,
            title = self.TITLE,
            clear = True,
            fg = (255, 255, 255),
            bg = (0, 0, 0),
        )

        console.print(x = x+1, y = 1, string = "Congratulations! You level up!")
        console.print(x = x+1, y = 2, string = "Select an attribute to increase.")

        console.print(
            x = x + 1,
            y = 4,
            string=f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )
        console.print(
            x = x + 1,
            y = 5,
            string=f"b) Strength (+1 attack, from {self.engine.player.fighter.power})",
        )
        console.print(
            x = x + 1,
            y = 6,
            string=f"c) Agility (+1 defense, from {self.engine.player.fighter.defense})",
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 2:
            if index == 0:
                player.level.increase_max_hp()
            elif index == 1:
                player.level.increase_power()
            else:
                player.level.increase_defense()
        
        else:
            self.engine.message_log.add_message('Invalid entry.', color.invalid)

            return None
        
        return super().ev_keydown(event)
    
    # Don't allow the player to click to exit the menu, like normal.
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        return None
    


"""
InventoryEventHandler class:
    Displays the player's inventory and allows selection of items.
    Inherits from AskUserEventHandler.

Attributes:
    TITLE (str):
        The title displayed at the top of the inventory window.

Methods:
    on_render:
        Renders the inventory menu to the console.

        Parameters:
            console (Console): The console to render the inventory menu.

        Return:
            > None

    ev_keydown:
        Handles keydown events to select an item from the inventory.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[ActionOrHandler]: Returns the result of on_item_selected() or None.

    on_item_selected:
        Called when the user selects a valid item.

        Parameters:
            item (Item): The selected item.

        Return:
            > Optional[ActionOrHandler]: Must be implemented by subclasses.
"""
class InventoryEventHandler(AskUserEventHandler):

    TITLE = "<missing title>"

    def on_render(self, console: tcod.console.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        heigt = number_of_items_in_inventory + 2
        
        if heigt <= 3:
            heigt = 3

        if self.engine.player.x <= 30:
            x = 40
        else :
            x = 0
        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=heigt,
            title=self.TITLE,
            clear=True,
            fg=(255,255,255),
            bg=(0,0,0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                
                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f'({item_key}) {item.name}'

                if is_equipped:
                    item_string = f'({item_string}) (E)'

                console.print(x + 1, y + i + 1, item_string)
        else :
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event : tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26 :
            try :
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)
    
    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()
    
"""
InventoryActivateHandler class:
    Handles using an item from the inventory.
    Inherits from InventoryEventHandler.

Methods:
    on_item_selected:
        Returns the action for the selected item.

        Parameters:
            item (Item): The selected item.

        Return:
            > Optional[ActionOrHandler]: The action associated with the item.
"""
class InventoryActivateHndler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return actions.EquipAction(self.engine.player, item)
        
        else:
            return None
    
"""
InventoryDropHandler class:
    Handles dropping an item from the inventory.
    Inherits from InventoryEventHandler.

Methods:
    on_item_selected:
        Creates an action to drop the selected item.

        Parameters:
            item (Item): The selected item.

        Return:
            > Optional[ActionOrHandler]: The action to drop the item.
"""
class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    TITLE = "Select n item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return actions.DropItem(self.engine.player, item)

"""
SelectIndexHandler class:
    Handles asking the user to select a tile index on the map.
    Inherits from AskUserEventHandler.

Methods:
    on_render:
        Highlights the tile under the cursor.

        Parameters:
            console (Console): The console to render the selection.

        Return:
            > None

    ev_keydown:
        Handles key movement and confirmation keys.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[ActionOrHandler]: Returns the result of on_index_selected() or None.

    ev_mousebuttondown:
        Handles mouse button down events to confirm selection.

        Parameters:
            event (tcod.event.MouseButtonDown): The mouse button down event.

        Return:
            > Optional[ActionOrHandler]: Returns the result of on_index_selected() or None.

    on_index_selected:
        Called when a tile index is selected.

        Parameters:
            x (int): The x coordinate of the selected tile.
            y (int): The y coordinate of the selected tile.

        Return:
            > Optional[ActionOrHandler]: Must be implemented by subclasses.
"""
class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""

        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1 # Holding modifier keys will speed up key movement.

            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier

            # Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))

            self.engine.mouse_location = x, y
            return None
        
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)
    
    def ev_mousebuttondown(
            self, event: tcod.event.MouseButtonDown
        ) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
            
        return super().ev_mousebuttondown(event)
    
    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()
    
"""
SingleRangedAttackHandler class:
    Handles targeting a single enemy with a callback for the action.
    Inherits from SelectIndexHandler.

Attributes:
    callback (Callable[[Tuple[int, int]], Optional[Action]]):
        A callback function to handle the action at the selected tile.

Methods:
    on_index_selected:
        Executes the callback with the coordinates of the selected tile.

        Parameters:
            x (int): The x coordinate of the selected tile.
            y (int): The y coordinate of the selected tile.

        Return:
            > Optional[Action]: The action returned by the callback.
"""
class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""
    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)

"""
SingleRangedAttackHandler class:
    Handles targeting a single enemy with a callback for the action.
    Inherits from SelectIndexHandler.

Attributes:
    callback (Callable[[Tuple[int, int]], Optional[Action]]):
        A callback function to handle the action at the selected tile.

Methods:
    on_index_selected:
        Executes the callback with the coordinates of the selected tile.

        Parameters:
            x (int): The x coordinate of the selected tile.
            y (int): The y coordinate of the selected tile.

        Return:
            > Optional[Action]: The action returned by the callback.
"""
class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""
    def __init__(
            self, engine: Engine, callback: callable[[Tuple[int, int]], Optional[Action]]
        ):
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))

"""
AreaRangedAttackHandler class:
    Handles targeting an area within a given radius. Highlights the affected area.
    Inherits from SelectIndexHandler.

Attributes:
    radius (int):
        The radius of the area to be affected.

    callback (Callable[[Tuple[int, int]], Optional[Action]]:
        A callback function to handle the action in the targeted area.

Methods:
    on_render:
        Highlights the area within the radius around the cursor.

        Parameters:
            console (Console): The console to render the highlighted area.

        Return:
            > None

    on_index_selected:
        Executes the callback with the coordinates of the center of the area.

        Parameters:
            x (int): The x coordinate of the selected tile.
            y (int): The y coordinate of the selected tile.

        Return:
            > Optional[Action]: The action returned by the callback.
"""
class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self, 
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback
    
    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x = x - self.radius + 1,
            y = y - self.radius + 1,
            width= (self.radius) * 2 -1,
            height= (self.radius) * 2 -1,
            fg= color.red,
            clear=False,
        )
    
    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))
