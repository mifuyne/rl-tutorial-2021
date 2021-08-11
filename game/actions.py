# game/actions.py

from __future__ import annotations
from game.components.inventory import Inventory
from typing import Optional, Tuple, TYPE_CHECKING

import game.colour as colour
import game.exceptions as exceptions

if TYPE_CHECKING:
    from game.engine import Engine
    from game.entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self, engine: Engine, entity: Entity) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pick up an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        Inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(Inventory.items) >= Inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                Inventory.items.append(item)

                self.engine.message_log.add_message(
                    f"You picked up the {item.name}!")
                return

        return exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
            self,
            entity: Actor,
            item: Item,
            target_xy: Optional[Tuple[int, int]] = None
    ) -> None:
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the item's ability, this action will be given to provide context"""
        self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        self.entity.inventory.drop(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        return NotImplementedError()


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_colour = colour.player_atk
        else:
            attack_colour = colour.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_colour
                )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_colour
                )


class MoveAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:

        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MoveAction(self.entity, self.dx, self.dy).perform()

