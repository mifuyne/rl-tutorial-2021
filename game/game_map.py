# game/game_map.py

from __future__ import annotations

from typing import Iterable, Optional, TYPE_CHECKING

import numpy as np
from tcod.console import Console

import game.tile_types as tile_types

if TYPE_CHECKING:
    from game.entity import Entity

class GameMap:
    def __init__(self, width: int, height: int, entities: Iterable[Entity] = ()):
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height),
            fill_value=tile_types.wall, order="F")
        self.visible = np.full((width, height),
            fill_value=False, order="F")  # Visible to player
        self.explored = np.full((width, height),
            fill_value=False, order="F")  # previously explored

    def get_blocking_entity_at_location(
            self, location_x: int, location_y: int
            ) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.
 
        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".

        > Source: http://rogueliketutorials.com/tutorials/tcod/v2/part-4/
        """
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD
        )

        for entity in self.entities:
            # Print entities in view
            if self.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y,
                              entity.char, fg=entity.colour)
