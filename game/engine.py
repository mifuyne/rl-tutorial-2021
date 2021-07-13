# game/engine.py

from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console

from game.entity import Entity
from game.game_map import GameMap
from game.input_handlers import EventHandler


class Engine:
    def __init__(self, 
            entities: Set[Entity], event_handler: EventHandler,
            game_map: GameMap, player: Entity):
        self.entities = entities
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
    
    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event) # assigns Action object

            if action is None:
                continue

            action.perform(self, self.player) # ex: <MoveAction>.perform
    
    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        
        for entity in self.entities:
            console.print(
                x=entity.x, y=entity.y, string=entity.char, fg=entity.colour)
        
        context.present(console)
        console.clear()
