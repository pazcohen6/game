from enum import auto, Enum

"""
EquipmentType Enum:
    Defines different types of equipment a character can use.

Attributes:
    WEAPON:
        Represents weapons such as swords or bows.
        > auto() generates a unique integer value.

    ARMOR:
        Represents defensive gear like shields or helmets.
        > auto() generates a unique integer value.
"""
class EquipmentType(Enum):
    WEAPON = auto()
    ARMOR = auto()

