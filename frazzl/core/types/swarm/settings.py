from importlib import import_module

from frazzl.core.exceptions import ConfigError
from frazzl.core.util.class_defs import validate_class


@validate_class
class SwarmSetting:
    required_fields = []
    default_setting = None

    def __init__(self):
        pass

    @classmethod
    def validate(cls, definition):
        return {}


@validate_class
class Modules(SwarmSetting):
    setting_typename = "submodules"
    required_fields = ["submodules"]
    default_setting = ["app", "config"]

    def __init__(self, *args):
        super(Modules, self).__init__()
        self.search_attrs = args

    def search_submodules(self, module):
        sub_modules = {}
        for search_attr in self.search_attrs:
            try:
                sub_modules[search_attr] = import_module(f"{module.__name__}.{search_attr}")
            except ImportError:
                continue
        return sub_modules

    @classmethod
    def validate(cls, definition):
        if definition is not None and type(definition) is not list:
            raise ConfigError("If overwriting the modules setting, it must be a list in the settings file. "
                              f"Got {definition}")
        if not definition:
            definition = cls.default_setting

        if len(definition) <= 0:
            raise ConfigError("If overwriting the modules setting, it must define at least one module to search")

        return {"submodules": Modules(*definition)}


@validate_class
class SwarmSettings:
    setting_types = [Modules]

    @classmethod
    def validate(cls, swarm_definition):
        settings_definition = swarm_definition.get("settings", {})
        if settings_definition is not None and type(settings_definition) is not dict:
            raise ConfigError("A swarm that defines global settings should have settings attributes in its definition")

        for setting_type in cls.setting_types:
            setting_context = setting_type.validate(settings_definition.get(setting_type.setting_typename, None))
            cls.context.update(setting_context)

        return cls.context
