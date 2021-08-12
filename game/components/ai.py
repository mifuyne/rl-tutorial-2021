# game/components/ai.py

from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

from game.actions import (
    Action,
    BumpAction,
    MeleeAction,
    MoveAction,
    WaitAction
)

if TYPE_CHECKING:
    from game.entity import Actor


class BaseAI(Action):

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """
        Compute and return a path to the target position

        If there is no valid path, then returns an empty list
        """
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype = np.int8)

        # Checking against all existing entities in this level
        for entity in self.entity.gamemap.entities:
            # Adding a higher cost to encourage other entities to
            # take the longer path around
            if entity.blocks_movement and cost[entity.x, entity.y]:
                cost[entity.x, entity.y] += 10
        
        graph = tcod.path.SimpleGraph(cost = cost, cardinal = 2, diagonal = 3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y)) # Start position

        # Calculate the path to destination, remove starting point
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert List[List[int]] to List[Tuple[int, int]]
        return [(index[0], index[1]) for index in path]


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, 
    then revert back to its previous AI. If an actor occupies a tile it is 
    randomly moving into, it will attack.
    """

    def __init__(
            self, entity: Actor,
            previous_ai: Optional[BaseAI],
            turns_remaining: int
            ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Revert AI back to original state
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
                )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),
                    (0, -1),
                    (1, -1),
                    (-1, 0),
                    (-1, 1),
                    (-0, 1),
                    (1, 1),
                ]
            )

            self.turns_remaining -= 1

            # actor will try to move or attack in chosen random direction
            return BumpAction(self.entity, direction_x, direction_y,).perform()


class HostileEnemy(BaseAI):
    
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev/"Chessboard" Distance

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            # Attack if the distance between player and entity is less than 1
            # (right next to each other)
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            # player can see the entity, but too far away (move entity)
            self.path = self.get_path_to(target.x, target.y)

        # if entity has a path, move
        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MoveAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y
                ).perform()

        # If none of the above, wait
        return WaitAction(self.entity).perform()
