from classes import CombatMap, Player
import json
from typing import Any, Dict, List, Optional, Union, Tuple, Set
import combat_map_utils

Coord = Tuple[int, int] 

# Load the JSON file
with open("player1.json") as f:
    json_data = json.load(f)

# Create the players dict dynamically
players: Dict[str, Player] = {
    name: Player.from_dict(player_data)
    for name, player_data in json_data.items()
}
def get_zoc_tiles(enemy_pos: Coord, reach : int) -> set[Coord]:
    reach = reach
    x, y = enemy_pos
    return {
        (x + dx, y + dy)
        for dx in range(-reach, reach + 1)
        for dy in range(-reach, reach + 1)
        if (dx != 0 or dy != 0) and abs(dx) + abs(dy) <= reach
    }

def precompute_enemy_zocs(combat_map : CombatMap, players_dict: Player) -> Dict[Coord, Set[Coord]]:
    """
    Returns a dict mapping enemy position → set of tiles in their ZoC.
    """
    enemy_zocs = {}
    for pos, tile in combat_map.tiles.items():
        if tile.has_enemy:
            reach = players_dict[tile.entity].reach
            enemy_zocs[tile.entity] = get_zoc_tiles(pos, reach)
    return enemy_zocs

print(players)
instanced_map = CombatMap(width=30, height=30,players=players)

instanced_map.update_entities_on_map()

print(instanced_map)

def find_possible_positions_on_map(map: CombatMap, players_dict: dict, current_player : str) -> List[Coord]:
    current_pos = players[current_player].position
    movespeed = players[current_player].move_speed

    zocs = precompute_enemy_zocs(combat_map=map, players_dict=players)
    return zocs
    
print(find_possible_positions_on_map(instanced_map,players,"Kaelin"))




#map.apply_effect(x_center=15, y_center= 15, form="quadrat", size=5, effect="entangle")

#print(map)