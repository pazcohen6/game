from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Actor, Item

"""
Equipment class:
    Manages the equipment system, allowing actors to equip or unequip items.

Attributes:
    parent (Actor):
        Reference to the actor that owns this equipment.
    weapon (Optional[Item]):
        The currently equipped weapon, if any.
    armor (Optional[Item]):
        The currently equipped armor, if any.

Methods:
    defense_bonus:
        Calculates the total defense bonus from equipped items.

        Return:
            > int: Sum of defense bonuses from weapon and armor.

    power_bonus:
        Calculates the total power bonus from equipped items.

        Return:
            > int: Sum of power bonuses from weapon and armor.

    item_is_equipped:
        Checks if a given item is currently equipped.

        Parameters:
            item (Item): The item to check.

        Return:
            > bool: True if the item is equipped, False otherwise.

    unequip_message:
        Displays a message when an item is unequipped.

        Parameters:
            item_name (str): The name of the unequipped item.

        Return:
            > None

    equip_message:
        Displays a message when an item is equipped.

        Parameters:
            item_name (str): The name of the equipped item.

        Return:
            > None

    equip_to_slot:
        Equips an item to a specified slot, unequipping any current item in that slot.

        Parameters:
            slot (str): The equipment slot ("weapon" or "armor").
            item (Item): The item to equip.
            add_message (bool): Whether to display a message.

        Return:
            > None

    unequip_from_slot:
        Unequips an item from a specified slot.

        Parameters:
            slot (str): The equipment slot ("weapon" or "armor").
            add_message (bool): Whether to display a message.

        Return:
            > None

    toggle_equip:
        Toggles equipping or unequipping an item based on its current state.

        Parameters:
            equippable_item (Item): The item to equip or unequip.
            add_message (bool): Whether to display a message (default is True).

        Return:
            > None
"""
class Equipment(BaseComponent):
    parent: Actor

    def __init__(self, weapon: Optional[Item] = None, armor: Optional[Item] = None):
        self.weapon = weapon
        self.armor = armor

    @property
    def defense_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.defense_bonus
        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.defense_bonus

        return bonus
    
    @property
    def power_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.power_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.power_bonus

        return bonus
    
    def item_is_equipped(self, item: Item) -> bool:
        return self.weapon == item or self.armor == item
    
    def unequip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f'You remove the {item_name}.'
        )
    
    def equip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f'You equip the {item_name}.'
        )
        
    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)
        
        if current_item is not None:
            self.unequip_from_slot(slot, add_message)
        
        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)
        
    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        if (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.WEAPON
        ):
            slot = "weapon"

        else:
            slot = "armor"
        
        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)