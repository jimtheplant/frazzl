class FrazzlException(Exception):
    pass


class ConfigError(FrazzlException, RuntimeError):
    pass


class BuilderError(FrazzlException):
    pass
