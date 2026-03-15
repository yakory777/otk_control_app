import logging
import sys
from app.ui.main_window import run_app  # noqa: E402

logging.basicConfig(
    level=logging.DEBUG,
    format=(
        "%(asctime)s  %(levelname)-7s  "
        "%(name)s  %(message)s"
    ),
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logging.getLogger("fontTools").setLevel(
    logging.WARNING,
)


if __name__ == '__main__':
    run_app()
