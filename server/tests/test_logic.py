import pytest
from app.config import GameConfig
from app.state import GameState
from app.teams import TeamParams
from app.logic import GameLogic

def test_calculate_conversion_probability():
    config = GameConfig()
    state = GameState(config.WIDTH, config.HEIGHT)
    team_x = TeamParams(aggressiveness=1.0)
    team_y = TeamParams(aggressiveness=1.0)
    logic = GameLogic(state, team_x, team_y, config)

    prob_x = logic.calculate_conversion_probability("X", 5, 2)
    assert 0 <= prob_x <= 1

    prob_y = logic.calculate_conversion_probability("Y", 3, 3)
    assert 0 <= prob_y <= 1
