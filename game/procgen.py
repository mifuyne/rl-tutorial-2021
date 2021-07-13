# game/procgen.py

from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING

import tcod

from game.game_map import GameMap
import game.tile_types as tile_types

if TYPE_CHECKING:
    from entity import Entity

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2

        return center_x, center_y
    
    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return(
            self.x1 <= other.x2 and
            self.x2 >= other.x1 and
            self.y1 <= other.y2 and
            self.y2 >= other.y1
        )


def tunnel_between(
        start: Tuple[int, int], end: Tuple[int, int]
        ) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points"""

    x1, y1 = start
    x2, y2 = end

    if random.random() < 0.5:
        # dig horizontal, then vertical
        corner_x, corner_y = x2, y1
    else:
        # dig vertical, then horizontal
        corner_x, corner_y = x1, y2

    # Generate coordinates for the tunnel
    for x, y in tcod.los.bresenham(start, (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), end).tolist():
        yield x, y


def generate_dungeon(
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        player: Entity) -> GameMap:
    """Generate a new dungeon map"""
    dungeon = GameMap(map_width, map_height)

    rooms: List[RectangularRoom] = []

    for r in range(max_rooms):
        # size
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        # position
        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)
        
        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue # Intersection found, skip to the next attempt

        # Dig
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # Starting room (place player here)
            player.x, player.y = new_room.center
        else:
            # digging tunnels
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        # Add the new room to the rooms list
        rooms.append(new_room)
    
    return dungeon