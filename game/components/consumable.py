# game/components/consumable.py

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import game.actions as actions
import game.colour as colour
import game.components.inventory as inventory
from game.components.base_component import BaseComponent
from game.exceptions import Impossible

if TYPE_CHECKING:
    from entity import Actor, Item

class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.Itemaction) -> None:
        """Invoke this items ability.
        
        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inv_instance = entity.parent
        if isinstance(inv_instance, inventory.Inventory):
            inv_instance.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                colour.health_recovered
                )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")