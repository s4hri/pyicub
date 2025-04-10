import pytest
from examples.PositionController.move_head import move_head

@pytest.mark.smoke
def test_move_head_runs():
    try:
        move_head()
    except Exception as e:
        pytest.fail(f"move_head() raised an exception: {e}")

