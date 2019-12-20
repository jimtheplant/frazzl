from importlib import import_module

from frazzl.core.exceptions import ConfigError
from frazzl.core.util.class_defs import WithContext


class SwarmSetting(WithContext):
    setting_name = None

    def __init__(self, definition):
        super(SwarmSetting, self).__init__()
        self.context = SwarmSetting.validate(definition, self.context)

    @classmethod
    def validate(cls, definition, context):
        return {}


class Modules(SwarmSetting):
    setting_name = "submodules"

    def __init__(self, definition):
        super(Modules, self).__init__(definition)
        self.context = Modules.validate(definition, self.context)

    def search_submodules(self, module):
        sub_modules = []
        for search_attr in self.context[self.setting_name]:
            try:
                sub_modules.append(import_module(f"{module.__name__}.{search_attr}"))
            except ImportError:
                continue
        return sub_modules

    @classmethod
    def validate(cls, definition, context):
        if definition is not None and type(definition) is not list:
            raise ConfigError("If overwriting the modules setting, it must be a list in the settings file. "
                              f"Got {definition}")

        return {cls.setting_name: [] if not definition else definition}


class GatewayProtocol(SwarmSetting):
    setting_name = "gateway"
    default_setting = True

    def __init__(self, definition):
        super(GatewayProtocol, self).__init__(definition)
        self.context = GatewayProtocol.validate(definition, self.context)

    @classmethod
    def validate(cls, definition, context):
        if definition and len(definition) > 0:
            return {cls.setting_name: definition.lower() == "true"}
        return {cls.setting_name: cls.default_setting}


class SwarmSettings:
    setting_types = []

    def __init__(self, settings):
        self.__setting_instances = settings
        for setting_name, setting in settings.items():
            setattr(self.__class__, setting_name, property(lambda inst: setting.context[setting_name]))

    def __getitem__(self, item):
        return self.__setting_instances[item]

    @classmethod
    def validate(cls, settings_definition):
        if settings_definition is not None and type(settings_definition) is not dict:
            raise ConfigError("A swarm that defines global settings should have settings attributes in its definition")

        settings = {}
        for setting_type in cls.setting_types:
            settings[setting_type.setting_name] = setting_type(settings_definition.get(setting_type.setting_name, None))

        return SwarmSettings(settings)

    @classmethod
    def register_setting_types(cls, setting_types):
        for setting_type in setting_types:
            if setting_type not in cls.setting_types:
                cls.setting_types.append(setting_type)


SwarmSettings.register_setting_types([Modules, GatewayProtocol])
