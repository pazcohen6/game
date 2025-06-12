from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Item

"""
Equippable class:
    Represents an equippable item that provides bonuses to an actor's power, defense, and critical hit chance.

Attributes:
    parent (Item):
        Reference to the item that owns this equippable component.
    equipment_type (EquipmentType):
        The type of equipment (e.g., weapon or armor).
    power_bonus (int):
        The power bonus provided by the equippable item.
    defense_bonus (int):
        The defense bonus provided by the equippable item.
    critical_chance_bonus (int):
        The critical hit chance bonus provided by the equippable item.

Methods:
    __init__:
        Initializes an equippable item with type, power bonus, defense bonus, and critical chance bonus.

        Parameters:
            equipment_type (EquipmentType): The type of equipment (e.g., weapon, armor).
            power_bonus (int): The power bonus this item provides (default is 0).
            critical_chance_bonus (int): The critical hit chance bonus this item provides (default is 0).
            defense_bonus (int): The defense bonus this item provides (default is 0).
"""
class Equippable(BaseComponent):
    parent: Item

    def __init__(
            self,
            equipment_type: EquipmentType,
            power_bonus: int = 0,
            critical_chance_bonus: int = 0,
            defense_bonus: int = 0,
        ):
            self.equipment_type = equipment_type

            self.power_bonus = power_bonus
            self.defense_bonus = defense_bonus
            self.critical_chance_bonus = critical_chance_bonus
            
"""
Dagger class:
    Represents a dagger, a type of equippable weapon.

Methods:
    __init__:
        Initializes a dagger with a power bonus.
"""
class Dagger(Equippable):
     def __init__(self) -> None:
          super().__init__(equipment_type = EquipmentType.WEAPON, power_bonus = 2)

"""
Sword class:
    Represents a sword, a type of equippable weapon.

Methods:
    __init__:
        Initializes a sword with a power bonus.
"""
class Sword(Equippable):
     def __init__(self) -> None:
          super().__init__(equipment_type = EquipmentType.WEAPON, power_bonus = 4)

"""
LeatherArmor class:
    Represents leather armor, a type of equippable armor.

Methods:
    __init__:
        Initializes leather armor with a defense bonus.
"""
class LeatherArmor(Equippable):
     def __init__(self) -> None:
          super().__init__(equipment_type = EquipmentType.ARMOR, defense_bonus = 1)

"""
ChainMail class:
    Represents chain mail, a type of equippable armor.

Methods:
    __init__:
        Initializes chain mail with a defense bonus.
"""
class ChainMail(Equippable):
     def __init__(self) -> None:
          super().__init__(equipment_type = EquipmentType.ARMOR, defense_bonus = 3)