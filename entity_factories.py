from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from entity import Actor, Item
from components.inventory import Inventory
from components.level import Level

"""
entity_factories.py

This module defines instances of actors and items used in the game. 

Actors include the player and two types of enemies, each with specific attributes and behaviors.
Items include various consumables that can be used in the game.

Actors:
- Player: Character controlled by the player, with specified attributes and abilities.
- Orc: Basic enemy with minimal attributes.
- Troll: More powerful enemy with higher attributes.

Items:
- Health Potion: Consumable item that heals the player.
- Scroll of Lightning: Consumable item that deals lightning damage.
- Scroll of Confusion: Consumable item that confuses enemies.
- Scroll of Firecube: Consumable item that deals fire damage in a radius.

The following instances are created:
"""

# Player instance
player = Actor(
   char = "@",
   color = (255, 255, 255),
   name = "Player",
   ai_cls = HostileEnemy,
   fighter = Fighter(hp=30, defense=2, power=5),
   inventory = Inventory(capacity=26),
   level = Level(level_up_base = 200),
)

# Enemys
# Orc enemy instance
orc = Actor(
   char = "o",
   color = (63, 127, 63),
   name = "Orc",
   ai_cls = HostileEnemy,
   fighter = Fighter(hp = 10, defense = 0, power = 3),
   inventory = Inventory(capacity = 0),
   level = Level(xp_given = 35),
)

# Troll enemy instance
troll = Actor(
   char = "T",
   color = (0, 127, 0),
   name = "Troll",
   ai_cls = HostileEnemy,
   fighter = Fighter(hp = 16, defense = 1, power = 4),
   inventory = Inventory(capacity = 0),
   level = Level(xp_given = 100),
)

# Items
# Health Potion item instance
health_potion = Item(
   char = "!",
   color = (127,0,255),
   name = "Health Potion",
   consumable = consumable.HealingConsumable(amount = 4),
)

# Scroll of Lightning item instance
lightning_scroll = Item(
   char="~",
   color=(255,255,00),
   name="Scroll of Lightning",
   consumable= consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)

# Scroll of Confusion item instance
confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name= "Scroll of Confusion",
    consumable= consumable.ConfusionConsumable(number_of_turns=10),
)

# Scroll of Firecube item instance
firecube_scroll = Item(
    char="~",
    color=(255,0,0),
    name="Scroll of Firecube",
    consumable=consumable.FirecubeDamageConsumable(damage=12, radius=3)
)
