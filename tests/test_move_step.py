
# test_move_step_smoke.py

import pytest
from examples.PositionController.move_step import HeadTorsoStep, iCub

@pytest.mark.smoke
def test_move_step_runs():
    """
    Smoke test to verify that moveStep can be executed
    without raising exceptions.
    """
    robot = iCub()
    step = HeadTorsoStep()
    try:
        robot.moveStep(step)
    except Exception as e:
        pytest.fail(f"moveStep execution failed with exception: {e}")
