import random

class TeamParams:
    def __init__(self, aggressiveness: float = 1.0):
        self.aggressiveness = aggressiveness
        self.last_cell_count = None

    def update_strategy(self, current_cell_count: int):
        if self.last_cell_count is None:
            self.last_cell_count = current_cell_count
            return

        if current_cell_count < self.last_cell_count:
            loss_ratio = (self.last_cell_count - current_cell_count) / self.last_cell_count
            increase_factor = 1.0 + 0.2 * loss_ratio
            self.aggressiveness = min(2.0, self.aggressiveness * increase_factor)
        
        elif current_cell_count > self.last_cell_count:
            gain_ratio = (current_cell_count - self.last_cell_count) / self.last_cell_count
            decrease_factor = 1.0 - 0.1 * gain_ratio
            self.aggressiveness = max(0.1, self.aggressiveness * decrease_factor)
        
        else:
            factor = random.uniform(0.98, 1.02)
            self.aggressiveness = max(0.1, min(2.0, self.aggressiveness * factor))

        self.last_cell_count = current_cell_count
        
    def mutate(self):
        factor = random.uniform(0.95, 1.05)
        self.aggressiveness = max(0.1, min(2.0, self.aggressiveness * factor))
