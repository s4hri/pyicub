
# tests/test_move_request_smoke.py

import pytest
from examples.PositionController.move_request import execute_fullbody_step_with_request

@pytest.mark.smoke
def test_execute_step_does_not_crash():
    """
    Smoke test to ensure that executing the full-body step
    returns motion requests and does not raise any exceptions.
    """
    try:
        requests = execute_fullbody_step_with_request()
        assert isinstance(requests, list), "Expected a list of motion requests"
        assert len(requests) > 0, "Expected at least one motion request"
    except Exception as e:
        pytest.fail(f"Execution failed: {e}")
