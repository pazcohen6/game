from enum import auto, Enum

"""
RendrOrder Enum:
    Specifies the rendering order for different types of game entities.
    
    Attributes:
        CORPSE:
            Represents the rendering order for corpse entities.
        ITEM:
            Represents the rendering order for item entities.
        ACTOR:
            Represents the rendering order for actor entities.
"""
class RendrOrder(Enum):
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()