import random

from .scenarios import SCENARIOS


def get_scenario(exclude_id=None):
    pool = [item for item in SCENARIOS if item['id'] != exclude_id] or SCENARIOS
    return random.choice(pool)
