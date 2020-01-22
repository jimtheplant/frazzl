import logging

# For logging within a frazzl application
FRAZZL_LOGGER = logging.getLogger("frazzl")

std_handler = logging.StreamHandler()
std_handler.setLevel(logging.INFO)

std_format = logging.Formatter(fmt="%(levelname)s - frazzl (%(process)d)| %(message)s")

std_handler.setFormatter(std_format)

FRAZZL_LOGGER.addHandler(std_handler)

# Better printing in the cli
CLI_LOGGER = logging.getLogger("frazzl-cli")
std_handler = logging.StreamHandler()

std_format = logging.Formatter(fmt="%(levelname)s: %(message)s")

std_handler.setFormatter(std_format)

CLI_LOGGER.addHandler(std_handler)
