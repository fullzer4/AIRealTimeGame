class GameConfig:
    WIDTH = 100
    HEIGHT = 100
    TICK_RATE = 0.002
    INITIAL_TEAM_X_AGG = 1.5
    INITIAL_TEAM_Y_AGG = 1.5
    BASE_CONVERSION_PROB = 0.5

    def __init__(self):
        self.game_ended = False