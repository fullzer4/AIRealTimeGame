import numpy as np

class GameState:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        total_cells = width * height
        half = total_cells // 2
        arr = np.array([1]*half + [2]*(total_cells - half))
        np.random.shuffle(arr)
        
        self.grid = arr.reshape((height, width))

    def get_cell(self, r: int, c: int) -> int:
        return self.grid[r, c]

    def set_cell(self, r: int, c: int, val: int):
        self.grid[r, c] = val

    def count_team_cells(self, team: int) -> int:
        return np.count_nonzero(self.grid == team)

    def copy_grid(self):
        return self.grid.copy()