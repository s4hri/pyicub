import pytest

@pytest.mark.smoke
def test_print_version(capsys):
    import pyicub
    pyicub.print_version()
    captured = capsys.readouterr()
    assert pyicub.__version__ in captured.out
