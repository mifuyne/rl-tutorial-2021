# game/entity_factories.py


from game.components.ai import HostileEnemy
from game.components import consumable, equippable
from game.components.equipment import Equipment
from game.components.fighter import Fighter
from game.components.inventory import Inventory
from game.components.level import Level
from game.entity import Actor, Item

player = Actor(
    char = "@", 
    colour = (255,255,255), 
    name = "Player",
    ai_cls = HostileEnemy,
    equipment = Equipment(),
    fighter = Fighter(hp = 30, base_defense = 1, base_power = 2),
    inventory = Inventory(capacity = 26),
    level = Level(level_up_base = 200)
    )

orc = Actor(
    char = "o", 
    colour = (63, 127, 63), 
    name = "Orc", 
    ai_cls = HostileEnemy,
    equipment = Equipment(),
    fighter = Fighter(hp = 10, base_defense = 0, base_power = 3),
    inventory = Inventory(capacity=0),
    level = Level(xp_given = 35)
    )
    
troll = Actor(
    char = "T", 
    colour = (0, 127, 0), 
    name = "Troll", 
    ai_cls = HostileEnemy,
    equipment = Equipment(),
    fighter = Fighter(hp = 16, base_defense = 1, base_power = 4),
    inventory = Inventory(capacity=0),
    level = Level(xp_given = 100)
    )

confusion_scroll = Item(
    char = "~",
    colour = (207, 63, 255),
    name = "Confusion Scroll",
    consumable = consumable.ConfusionConsumable(number_of_turns = 10),
)

fireball_scroll = Item(
    char = "~",
    colour = (255, 0, 0),
    name = "Fireball Scroll",
    consumable = consumable.FireballDamageConsumable(damage = 12, radius = 3),
)


health_potion = Item(
    char = "!",
    colour = (127, 0, 255),
    name = "Health Potion",
    consumable = consumable.HealingConsumable(amount = 4),
    )


lightning_scroll = Item(
    char = "~",
    colour = (255, 255, 0),
    name = "Lightning Scroll",
    consumable = consumable.LightningDamageConsumable(damage = 20, maximum_range = 5)
)


dagger = Item(
    char = "/",
    colour = (0, 191, 255),
    name = "Dagger",
    equippable = equippable.Dagger()
)

sword = Item(
    char = "/",
    colour = (0, 191, 255),
    name = "Sword",
    equippable = equippable.Sword()
)

leather_armor = Item(
    char = "[",
    colour = (139, 69, 19),
    name = "Leather Armor",
    equippable = equippable.LeatherArmor(),
)

chain_mail = Item(
    char = "[",
    colour = (139, 69, 19),
    name = "Chain Mail",
    equippable = equippable.ChainMail()
)
