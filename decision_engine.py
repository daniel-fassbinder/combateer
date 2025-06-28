from typing import Dict, Tuple, List
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import json


import combat_map_utils

Coord = Tuple[int, int]  # (x, y) Position

class Tile:
    def __init__(self):
        self.effects: List[str] = []
        self.entity: str

    def apply_effect(self, effect: str):
        self.effects.append(effect)

    def place_entity(self, entity_name: str):
        self.entity = entity_name

    def __repr__(self):
        return f"Tile(effects={self.effects})"

class CombatMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: Dict[Coord, Tile] = {
            (x, y): Tile() for y in range(height) for x in range(width)
        }

    def get_tile(self, x: int, y: int) -> Tile:
        return self.tiles[(x, y)]

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
            " ".join(f"{self.tiles[(x, y)].effects or '.'}" for x in range(self.width))
            for y in range(self.height)
        )
    

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

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any

@dataclass
class Player:
    name: str
    position: Coord
    hp: int
    max_hp: int
    ac: int
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
            actions=actions,
            effects=data.get("effects", []),
            saves=data.get("saves", {}),
            move_speed=data.get("move_speed", 30),
            spell_slots={int(k): v for k, v in data.get("spell_slots", {}).items()}
        )


class PlayerManager:
    def __init__(self):
        self.players: Dict[str, Player] = {}

    def add_player(self, player: Player):
        self.players[player.name] = player

    def remove_player(self, name: str):
        if name in self.players:
            del self.players[name]

    def get_player(self, name: str) -> Optional[Player]:
        return self.players.get(name)

    def all_players(self) -> List[Player]:
        return list(self.players.values())

    def to_dict(self) -> Dict[str, dict]:
        return {name: player.to_dict() for name, player in self.players.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, dict]) -> "PlayerManager":
        manager = cls()
        for name, player_data in data.items():
            manager.add_player(Player.from_dict(player_data))
        return manager

    def save_to_file(self, filename: str):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> "PlayerManager":
        with open(filename) as f:
            data = json.load(f)
        return cls.from_dict(data)

manager = PlayerManager.load_from_file("player1.json")

# Load the JSON file
with open("player1.json") as f:
    json_data = json.load(f)

# Create the players dict dynamically
players: Dict[str, Player] = {
    name: Player.from_dict(player_data)
    for name, player_data in json_data.items()
}

print(players)



def find_possible_positions_on_map(map: CombatMap, movespeed: int, current_player : str) -> List[Coord]:
    pass



#map = CombatMap(width=30, height=30)

#map.apply_effect(x_center=15, y_center= 15, form="quadrat", size=5, effect="entangle")

#print(map)