import random
import numpy as np
from state import GameState
from teams import TeamParams
from config import GameConfig

class GameLogic:
    def __init__(self, state: GameState, team_x: TeamParams, team_y: TeamParams, config: GameConfig):
        self.state = state
        self.team_x = team_x
        self.team_y = team_y
        self.config = config
        self.pulse_x = 0.0
        self.pulse_y = 0.0

    def neighbors_coords(self, r: int, c: int):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.config.HEIGHT and 0 <= nc < self.config.WIDTH:
                    yield nr, nc

    def largest_cluster_size(self, cells):
        if not cells:
            return 0
        visited = set()
        max_size = 0
        cells_set = set(cells)
        directions = [(1,0),(-1,0),(0,1),(0,-1)]

        for cell in cells:
            if cell not in visited:
                queue = [cell]
                visited.add(cell)
                size = 1
                while queue:
                    cr, cc = queue.pop()
                    for dr, dc in directions:
                        rr, cc2 = cr+dr, cc+dc
                        if (rr, cc2) in cells_set and (rr, cc2) not in visited:
                            visited.add((rr, cc2))
                            queue.append((rr, cc2))
                            size += 1
                if size > max_size:
                    max_size = size
        return max_size

    def calculate_local_weights(self, r: int, c: int):
        grid = self.state.grid
        neigh_coords = list(self.neighbors_coords(r, c))
        
        x_cells = []
        y_cells = []
        for nr, nc in neigh_coords:
            val = grid[nr, nc]
            if val == 1:
                x_cells.append((nr, nc))
            elif val == 2:
                y_cells.append((nr, nc))

        count_x = len(x_cells)
        count_y = len(y_cells)

        cluster_x = self.largest_cluster_size(x_cells)
        cluster_y = self.largest_cluster_size(y_cells)
        
        x_advantage = (count_x - count_y) + (0.1 * cluster_x)
        y_advantage = (count_y - count_x) + (0.1 * cluster_y)

        if count_x > count_y:
            fraction_x = count_x / 8.0
            if fraction_x > 0.8:
                x_advantage += 2.0
        elif count_y > count_x:
            fraction_y = count_y / 8.0
            if fraction_y > 0.8:
                y_advantage += 2.0

        return x_advantage, y_advantage

    def calculate_conversion_probability(self, team: str, advantage: float) -> float:
        base = self.config.BASE_CONVERSION_PROB * (1 + advantage * 0.3)
        if team == "X":
            return min(1.0, base * (self.team_x.aggressiveness + self.pulse_x))
        else:
            return min(1.0, base * (self.team_y.aggressiveness + self.pulse_y))

    def update_grid_once(self):
        grid = self.state.grid
        new_grid = grid.copy()
        height, width = grid.shape

        for r in range(height):
            for c in range(width):
                cell = grid[r, c]
                x_adv, y_adv = self.calculate_local_weights(r, c)

                x_adv *= 2
                y_adv *= 2

                if x_adv > y_adv and cell != 1:
                    prob = self.calculate_conversion_probability("X", x_adv - y_adv)
                    if prob > 0.8 or random.random() < prob:
                        new_grid[r, c] = 1
                elif y_adv > x_adv and cell != 2:
                    prob = self.calculate_conversion_probability("Y", y_adv - x_adv)
                    if prob > 0.8 or random.random() < prob:
                        new_grid[r, c] = 2
                else:
                    if x_adv == y_adv and x_adv != 0:
                        ratio = (self.team_x.aggressiveness + self.pulse_x) - (self.team_y.aggressiveness + self.pulse_y)
                        if ratio > 0 and cell != 1:
                            new_grid[r, c] = 1
                        elif ratio < 0 and cell != 2:
                            new_grid[r, c] = 2

        self.state.grid = new_grid

    def update_grid(self, iteration: int):
        for _ in range(3):
            self.update_grid_once()

        if iteration % 200 == 0:
            if random.random() < 0.5:
                self.pulse_x = 0.5
                self.pulse_y = 0.0
            else:
                self.pulse_y = 0.5
                self.pulse_x = 0.0

        self.pulse_x = max(0, self.pulse_x - 0.01)
        self.pulse_y = max(0, self.pulse_y - 0.01)

        grid = self.state.grid
        total = grid.size
        x_count = (grid == 1).sum()
        y_count = (grid == 2).sum()
        if x_count > 0.9 * total or y_count > 0.9 * total:
            self.config.game_ended = True