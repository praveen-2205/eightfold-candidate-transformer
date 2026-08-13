from candidate_transformer import __version__
from candidate_transformer.cli import main
from candidate_transformer.util.logging import get_logger

def test_import():
    assert isinstance(__version__, str)
    assert len(__version__) > 0

def test_cli_version(capsys):
    exit_code = main(["--version"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out

def test_logger_no_duplicate_handlers():
    log1 = get_logger("test_dup")
    log2 = get_logger("test_dup")
    assert log1 is log2
    assert len(log1.handlers) == 1