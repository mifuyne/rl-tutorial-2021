# game/components/ai.py

from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

from game.actions import Action, MeleeAction, MoveAction, WaitAction

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
