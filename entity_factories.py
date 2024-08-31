from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from entity import Actor, Item
from components.inventory import Inventory
"""
Actor instances for the game.

The following actors are defined: the player and two types of enemies .
"""
player = Actor(
   char="@",
   color=(255, 255, 255),
   name="Player",
   ai_cls=HostileEnemy,
   fighter=Fighter(hp=30, defense=2, power=5),
   inventory=Inventory(capacity=26),
)

# Enemys
orc = Actor(
   char="o",
   color=(63, 127, 63),
   name="Orc",
   ai_cls=HostileEnemy,
   fighter=Fighter(hp=10, defense=0, power=3),
   inventory=Inventory(capacity=0),
)

troll = Actor(
   char="T",
   color=(0, 127, 0),
   name="Troll",
   ai_cls=HostileEnemy,
   fighter=Fighter(hp=16, defense=1, power=4),
   inventory=Inventory(capacity=0),
)
# Items
health_potion = Item(
   char="!",
   color=(127,0,255),
   name="Health Potion",
   consumable= consumable.HealingConsumable(amount=4),
)

lightning_scroll = Item(
   char="~",
   color=(255,255,00),
   name="Scroll of Lightning",
   consumable= consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name= "Scroll of Confusion",
    consumable= consumable.ConfusionConsumable(number_of_turns=10),
)

firecube_scroll = Item(
    char="~",
    color=(255,0,0),
    name="Scroll of Firecube",
    consumable=consumable.FirecubeDamageConsumable(damage=12, radius=3)
)
