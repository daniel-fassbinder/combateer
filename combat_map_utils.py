from typing import List, Tuple
import math
from collections import deque, defaultdict
from typing import Dict, List, Tuple, Set

Coord = Tuple[int, int]

def get_area_coords(center: Coord, size: int, form: str) -> List[Coord]:
    cx, cy = center
    coords: List[Coord] = []

    if form == "quadrat":
        half = size // 2
        x_start = cx - half
        y_start = cy - half
        x_end = x_start + size - 1
        y_end = y_start + size - 1

        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                coords.append((x, y))

    elif form == "kreis":
        radius = size
        for x in range(cx - radius, cx + radius):
            for y in range(cy - radius, cy + radius):
                if math.dist((cx, cy), (x, y)) <= radius -1:
                    coords.append((x, y))

    else:
        raise ValueError(f"Unbekannte Form: {form}")

    return coords

def visualize_area_on_board(area_coords: List[Tuple[int, int]], board_size: int = 30, marker: str = "X") -> None:
    board = [["." for _ in range(board_size)] for _ in range(board_size)]

    for x, y in area_coords:
        if 0 <= x < board_size and 0 <= y < board_size:
            board[y][x] = marker  # Achtung: y ist Zeile, x ist Spalte

    for row in board:
        print(" ".join(row))



