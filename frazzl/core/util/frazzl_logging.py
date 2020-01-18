import logging

FRAZZL_LOGGER = logging.getLogger("frazzl")

std_handler = logging.StreamHandler()
std_handler.setLevel(logging.INFO)

std_format = logging.Formatter(fmt="%(levelname)s - frazzl (%(process)d)| %(message)s")

std_handler.setFormatter(std_format)

FRAZZL_LOGGER.addHandler(std_handler)
