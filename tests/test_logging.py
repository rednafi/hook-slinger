import logging
from unittest.mock import patch

from rich.logging import RichHandler

import app


@patch("app.LOG_LEVEL", "DEBUG")
def test_logging(capsys):
    assert app.LOG_LEVEL == "DEBUG"
    assert isinstance(app.logging.root.handlers[0], RichHandler)

    app.logging.root.setLevel(logging.DEBUG)
    assert app.logging.root.getEffectiveLevel() == logging.DEBUG

    for name in logging.root.manager.loggerDict.keys():
        assert logging.getLogger(name).handlers == []
        assert logging.getLogger(name).propagate is True

    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")

    out, err = capsys.readouterr()
    assert err == ""
    for message in ("debug", "info", "error", "critical"):
        assert message in out
