import copy
import types


def stringify_dict(data, indent=0):
    tabs = '\t' * indent
    data_str = f"{tabs}"
    for k, v in data.items():
        data_str += str(k) + "\n"
        if type(v) is list:
            data_str += ":\n"
            for item in v:
                data_str += f"\t{str(item)}\n"
        elif type(v) is dict:
            data_str += stringify_dict(v, indent + 1)
        else:
            data_str += f": {str(v)}\n"
    return data_str

class Context:
    def __init__(self):
        self.context = {}

    def __getitem__(self, item):
        return self.context[item]

    def __getattr__(self, item):
        return self.context.get(item)

    def update(self, other):
        if type(other) is dict:
            self.context.update(other)
        elif isinstance(other, Context):
            self.context.update(other.context)
        else:
            raise ValueError()

    def __str__(self):
        return stringify_dict(self.context)


class WithContext:
    def __init__(self):
        self._context = Context()

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        if type(value) is dict:
            self._context.update(value)
        elif isinstance(value, WithContext):
            self._context.update(value.context)
        else:
            raise ValueError()


class Build:
    def __init__(self, klass):
        if type(klass.build) is Build:
            self.builder_method = types.FunctionType(klass.build.builder_method.__code__,
                                                     klass.build.builder_method.__globals__)
        else:
            self.builder_method = types.FunctionType(klass.build.__code__, klass.build.__globals__)
        self.klass = klass

    def __call__(self, context):
        validated = self.klass.validate(context)
        validated_copy = copy.deepcopy(validated)
        ctx = self.builder_method(self.klass, validated_copy)
        return self.klass(ctx)


class FrazzlBuilder(WithContext):
    def __init__(self, context):
        super(FrazzlBuilder, self).__init__()
        self.context = context

    def __init_subclass__(cls, **kwargs):
        if cls.__init__ is not FrazzlBuilder.__init__:
            raise ValueError()
        super().__init_subclass__(**kwargs)
        cls.build = Build(cls)

    @classmethod
    def build(cls, context):
        raise NotImplementedError

    @classmethod
    def validate(cls, definition):
        raise NotImplementedError
