import pytest
from examples.PositionController.move_head_timeout import move_head_with_timeout

@pytest.mark.smoke
def test_move_head_timeout_runs():
    try:
        move_head_with_timeout()
    except Exception as e:
        pytest.fail(f"move_head_with_timeout() raised an exception: {e}")

