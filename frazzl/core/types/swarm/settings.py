from frazzl.core.exceptions import ConfigError
from frazzl.core.util.class_defs import FrazzlBuilder


class SwarmSetting(FrazzlBuilder):
    setting_key = None

    @classmethod
    def build(cls, context):
        return context

    @classmethod
    def validate(cls, definition):
        return {}


# TODO: Move Node settings to use builder such as SwarmSettings
# class Port(SwarmSetting):
#     @classmethod
#     def validate(cls, definition):
#         port = definition.get("port", None)
#         try:
#             port = int(port)
#         except ValueError:
#             raise ConfigError(f"Port given was not valid. Got: {port}")
#         return {"port": port}


class Environment(SwarmSetting):

    @classmethod
    def build(cls, context):
        logging_definition = context[LoggingConfig.setting_key]
        context[LoggingConfig.setting_key] = LoggingConfig.build(logging_definition)
        return context

    @classmethod
    def validate(cls, definition):
        if LoggingConfig.setting_key not in definition.keys():
            raise ConfigError(f"The {cls.setting_key} environment must specify a logging level.")

        LoggingConfig.validate(definition[LoggingConfig.setting_key])
        return definition


class Development(Environment):
    setting_key = "development"


class LoggingConfig(SwarmSetting):
    setting_key = "loggingLevel"
    logging_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

    @classmethod
    def build(cls, context):
        # TODO: Add logging
        return context

    @classmethod
    def validate(cls, definition):
        if definition not in cls.logging_levels:
            raise ConfigError(f"Must specify a valid logging level. Got: {definition}, "
                              f"Options {cls.logging_levels}")

        return {cls.setting_key: definition}


class EnvironmentSetting(SwarmSetting):
    setting_key = "environment"

    environment_types = [Development.setting_key]

    @classmethod
    def validate(cls, definition):
        if definition not in cls.environment_types:
            raise ConfigError(f"Environment setting must be one of the following: {cls.environment_types}")
        return {cls.setting_key: definition}


class SwarmSettings(FrazzlBuilder):
    environments = {env.setting_key: env for env in [Development]}

    @classmethod
    def validate(cls, definition):
        if definition is not None and type(definition) is not dict:
            raise ConfigError("The swarm did not define any global settings or the settings were not valid. "
                              "Make sure you have run: \n\tfrazzl init\n"
                              "to ensure the default profile has been created.")

        env = definition.get("environment", None)
        if not env:
            raise ConfigError("The environment field was not found on the settings definition.")

        EnvironmentSetting.validate(env)
        cls.environments[env].validate(definition[env])
        return definition

    @classmethod
    def build(cls, context):
        environment_setting = EnvironmentSetting.build(context[EnvironmentSetting.setting_key])
        environment_type = cls.environments[environment_setting.context[EnvironmentSetting.setting_key]]
        environment = environment_type.build(context[environment_type.setting_key])
        return {EnvironmentSetting.setting_key: environment_setting, environment_type.setting_key: environment}

