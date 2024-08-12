from typing import List, Reversible, Tuple
import textwrap

import tcod
import color

"""
Message class:
    Represents a single message with text and color. Optionally, it can keep
    track of how many times the message has been added if stacked.

Attributes:
    plain_text (str):
        The plain text of the message.
    fg (Tuple[int, int, int]):
        The foreground color of the message.
    count (int):
        The number of times this message has been stacked.

Methods:
    full_text:
        The full text of this message, including the count if necessary.

        Return:
            > str
"""
class Message:
    def __init__(self, text: str, fg: Tuple[int,int,int]):
        self.plain_text = text
        self.fg = fg
        self.count = 1
    
    @property
    def full_text(self) -> str:
        """The full text of this message, including the count if necessary."""
        if self.count > 1:
            return f"{self.plain_text} x({self.count})"
        return self.plain_text

"""
MessageLog class:
    Manages a collection of messages, allowing new messages to be added
    and rendered to a console. Messages can be stacked if they have the
    same text.

Attributes:
    messages (List[Message]):
        A list of messages in the log.

Methods:
    add_message:
        Add a message to this log. The message can be stacked with a previous
        message of the same text if `stack` is True.

        Parameters:
            text (str): The message text.
            fg (Tuple[int, int, int]): The text color.
            stack (bool): Whether to stack the message with a previous message.

        Return:
            > None

    render:
        Render the message log over the specified area of the console.

        Parameters:
            console (tcod.console.Console): The console to render onto.
            x (int): The x-coordinate of the rendering area.
            y (int): The y-coordinate of the rendering area.
            width (int): The width of the rendering area.
            height (int): The height of the rendering area.

        Return:
            > None

    render_messages:
        Render the provided messages onto the console, starting from the last message
        and working backwards.

        Parameters:
            console (tcod.console.Console): The console to render onto.
            x (int): The x-coordinate of the rendering area.
            y (int): The y-coordinate of the rendering area.
            width (int): The width of the rendering area.
            height (int): The height of the rendering area.
            messages (Reversible[Message]): The messages to render.

        Return:
            > None
"""    
class MessageLog:
    def __init__(self) -> None :
        self.messages: List[Message] = []

    def add_messge(
            self, text: str, fg: Tuple[int,int,int] = color.white, *, stack: bool = True
    ) -> None:
        """Add a message to this log.
        `text` is the message text, `fg` is the text color.
        If `stack` is True then the message can stack with a previous message
        of the same text.
        """
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count +=1
        else :
            self.messages.append(Message(text, fg))

    def render(
            self, console: tcod.console.Console, x: int, y: int, width: int, height: int,
    ) -> None:
        """Render this log over the given area.
        `x`, `y`, `width`, `height` is the rectangular region to render onto
        the `console`.
        """
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def render_messages(
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        """Render the messages provided.
        The `messages` are rendered starting at the last message and working
        backwards.
        """
        y_offset = height - 1

        for message in reversed(messages):
            for line in reversed(textwrap.wrap(message.full_text, width)):
                console.print(x= x, y= y + y_offset, string = line, fg = message.fg)
                y_offset -= 1
                if y_offset < 0 :
                    return
