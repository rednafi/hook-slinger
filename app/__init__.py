"""Here, the root logger is overriden to achieve ubiquitous custom log messages."""

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

import config

LOG_LEVEL = logging.getLevelName(config.LOG_LEVEL)


console = Console(
    color_system="standard",
    force_terminal=True,
    tab_size=4,
    width=90,
)

install(console=console)

logHandler = RichHandler(
    rich_tracebacks=True,
    console=console,
    tracebacks_width=88,
    show_time=False,
)


# Intercept everything at the root logger.
logging.root.handlers = [logHandler]
logging.root.setLevel(LOG_LEVEL)

# Remove every other logger's handlers
# and propagate to root logger.
for name in logging.root.manager.loggerDict.keys():
    logging.getLogger(name).handlers = []
    logging.getLogger(name).propagate = True
