#!/usr/bin/env python3
# main.py

import tcod

from game.engine import Engine
from game.entity import Entity
from game.game_map import GameMap
from game.input_handlers import EventHandler

def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45

    tileset = tcod.tileset.load_tilesheet(
            "data/dejavu12x12_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    event_handler = EventHandler()

    player = Entity(
            screen_width // 2, screen_height // 2, "@", (255, 255, 255))
    npc = Entity(
        screen_width // 2 - 5, screen_height // 2, "@", (255, 255, 0))
    entities = {npc, player}

    game_map = GameMap(map_width, map_height)

    engine = Engine(entities=entities, 
            event_handler=event_handler, game_map=game_map, player=player)

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title="Maybe Cyberpunk Roguelike",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        while True:
            engine.render(console=root_console, context=context)

            events = tcod.event.wait()

            engine.handle_events(events)


if __name__ == "__main__":
    main()
