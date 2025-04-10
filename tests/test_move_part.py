
# tests/test_move_part_smoke.py

import pytest
from examples.PositionController.move_part import move_head_and_eyes

@pytest.mark.smoke
def test_move_head_and_eyes_runs():
    """
    Smoke test to ensure that moving the iCub's head and eyes
    completes without raising exceptions.
    """
    try:
        move_head_and_eyes()
    except Exception as e:
        pytest.fail(f"move_head_and_eyes() raised an exception: {e}")
