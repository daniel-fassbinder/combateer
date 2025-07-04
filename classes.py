from typing import Dict, Tuple, List
from typing import Any, Dict, List, Optional, Union
import json
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any

import combat_map_utils

Coord = Tuple[int, int]  # (x, y) Position

@dataclass
class Action:
    type: str
    name: str
    action_type: str
    cost: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Action':
        type_map = {
            "MeleeAttack": MeleeAttack,
            "RangedAttack": RangedAttack,
            "Spell": Spell,
            "Grapple": Grapple,
            "Dash": Dash
        }
        cls = type_map.get(data["type"])
        if not cls:
            raise ValueError(f"Unknown action type: {data['type']}")
        return cls(**data)
    
@dataclass
class MeleeAttack(Action):
    to_hit_bonus: int
    damage_bonus: int
    damage_dice: str
    damage_type: str
    range: int = 5

@dataclass
class RangedAttack(Action):
    to_hit_bonus: int
    damage_dice: str
    damage_type: str
    range: int
    long_range: Optional[int] = None

@dataclass
class Spell(Action):
    level: int
    school: str
    components: List[str]
    range: int
    form: Optional[str] = None
    size: Optional[int] = None
    save_type: Optional[str] = None
    effect: Optional[str] = None

@dataclass
class Grapple(Action):
    dc: Optional[int] = None
    contested: bool = True

@dataclass
class Dash(Action):
    pass




@dataclass
class Player:
    name: str
    position: Coord
    hp: int
    max_hp: int
    ac: int
    reach: int
    is_enemy: bool
    actions: List[Action]
    effects: List[str] = field(default_factory=list)
    saves: Dict[str, int] = field(default_factory=dict)
    move_speed: int = 30
    spell_slots: Dict[int, int] = field(default_factory=dict)
    

    def is_alive(self) -> bool:
        return self.hp > 0

    def move(self, new_position: Coord):
        self.position = new_position

    def apply_effect(self, effect: str):
        if effect not in self.effects:
            self.effects.append(effect)

    def take_damage(self, amount: int):
        self.hp = max(self.hp - amount, 0)

    def heal(self, amount: int):
        self.hp = min(self.hp + amount, self.max_hp)

    def expend_spell_slot(self, level: int) -> bool:
        if self.spell_slots.get(level, 0) > 0:
            self.spell_slots[level] -= 1
            return True
        return False

    def __repr__(self):
        return (f"<Player {self.name} at {self.position} | HP: {self.hp}/{self.max_hp} | "
                f"Effects: {self.effects} | Spells: {self.spell_slots}>")

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Player':
        # Convert actions list to proper Action subclass instances
        actions = [Action.from_dict(a) for a in data.get("actions", [])]

        return Player(
            name=data["name"],
            position=tuple(data["position"]),
            hp=data["hp"],
            max_hp=data["max_hp"],
            ac=data["ac"],
            reach=data["reach"],
            is_enemy=data["is_enemy"],
            actions=actions,
            effects=data.get("effects", []),
            saves=data.get("saves", {}),
            move_speed=data.get("move_speed", 30),
            spell_slots={int(k): v for k, v in data.get("spell_slots", {}).items()}
        )


@dataclass
class Tile:
    effects: List[str] = field(default_factory=list)
    entity: str = ""
    move_cost : int = 1
    walkable : bool = True
    has_enemy: bool = False

    def apply_effect(self, effect: str):
        self.effects.append(effect)

    def place_entity(self, entity_name: str, enemy : bool):
        self.entity = entity_name
        if enemy:
            self.has_enemy = True
        else:
            self.has_enemy = False

class CombatMap:
    def __init__(self, width: int, height: int, players: Dict[str, Player]):
        self.width = width
        self.height = height
        self.players = players
        self.tiles: Dict[Coord, Tile] = {
            (x, y): Tile() for y in range(height) for x in range(width)
        }

    def update_entities_on_map(self):
        # Clear all entities and enemy flags on tiles
        for tile in self.tiles.values():
            tile.entity = ""
            tile.has_enemy = False

        # Place all players on their current positions
        for player_name, player in self.players.items():
            pos = player.position
            tile = self.tiles.get(pos)
            if tile:
                tile.place_entity(player_name, enemy=player.is_enemy)

    def get_tile(self, x: int, y: int) -> Tile:
        return self.tiles[(x, y)]
    
    def move_entity(self, start : Coord, end : Coord, entity_name: str):
        tile_start = self.tiles.get(start)
        tile_start.entity = ""
        tile_start.has_enemy = False

        tile_end = self.tiles.get(end)
        tile_end.entity = entity_name
        if self.players[entity_name].is_enemy:
            tile_end.has_enemy = True

    def apply_effect(self, x_center: int, y_center: int, form: str, size: int ,effect: str):
        affected_coords = combat_map_utils.get_area_coords(center=(x_center,y_center), size = size, form = form)
        for coord in affected_coords:
            tile = self.tiles.get(coord)
            if tile and effect not in tile.effects:
                tile.effects.append(effect)

    def __iter__(self):
        return iter(self.tiles.items())

    def __repr__(self):
        return "\n".join(
            " ".join(f"{self.tiles[(x, y)].effects or self.tiles[(x,y)].entity or '.'}" for x in range(self.width))
            for y in range(self.height)
        )
    

