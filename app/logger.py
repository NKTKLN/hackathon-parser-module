import logging


def setup_logger(
    disable_logging: bool = False, log_level: int = logging.INFO, log_file: str = ""
) -> None:
    if disable_logging:
        logging.disable(logging.CRITICAL)
        return

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level, format=log_format, filename=log_file, filemode="a"
    )
