import pytest
from examples.PositionController.move_parallel import move_head_and_torso_parallel

@pytest.mark.smoke
def test_move_head_and_torso_parallel_runs():
    try:
        move_head_and_torso_parallel()
    except Exception as e:
        pytest.fail(f"move_head_and_torso_parallel() raised an exception: {e}")

