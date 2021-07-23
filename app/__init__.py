import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

console = Console(color_system="standard", force_terminal=True, tab_size=4, width=90)

install(console=console)
logger = logging.getLogger("rq.worker")
logHandler = RichHandler(
    rich_tracebacks=True,
    console=console,
    tracebacks_width=88,
    show_time=False,
)
logger.addHandler(logHandler)
