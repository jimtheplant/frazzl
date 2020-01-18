import copy
import types

from frazzl.core.exceptions import BuilderError


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
    def __init__(self, context=None):
        self.__dict__["context"] = {}
        if context:
            self.update(context)

    def __getitem__(self, item):
        return self.context[item]

    def __setitem__(self, key, value):
        self.__dict__["context"][key] = value

    def __getattr__(self, item):
        return self.context.get(item)

    def __setattr__(self, key, value):
        self.__dict__["context"][key] = value

    def update(self, other):
        if type(other) is dict:
            self.context.update(other)
        elif isinstance(other, Context):
            self.context.update(other.context)
        else:
            raise ValueError(f"Attempt to update {other} failed. Not a dictionary or Context object")

    def __str__(self):
        return stringify_dict(self.context)


class WithContext:
    def __init__(self):
        self._context = Context()

    def __getattr__(self, item):
        try:
            return self._context[item]
        except KeyError:
            raise AttributeError(f"{self} has no attribute {item}.")

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        if type(value) is dict or isinstance(value, Context):
            self._context.update(value)
        elif isinstance(value, WithContext):
            self._context.update(value.context)
        else:
            raise ValueError(f"{value} was not a dictionary, WithContext, or Context object.")


class Build:
    def __init__(self, klass):
        if type(klass.build) is Build:
            self.builder_method = types.FunctionType(klass.build.builder_method.__code__,
                                                     klass.build.builder_method.__globals__)
        else:
            self.builder_method = types.FunctionType(klass.build.__code__, klass.build.__globals__)
        self.klass = klass

    def __call__(self, context, **kwargs):
        validated = self.klass.validate(context)
        validated_copy = copy.deepcopy(validated)
        ctx = self.builder_method(self.klass, Context(validated_copy), **kwargs)
        return self.klass(Context(context=ctx))


class FrazzlBuilder(WithContext):
    def __init__(self, context):
        super(FrazzlBuilder, self).__init__()
        self.context = context

    def __init_subclass__(cls, **kwargs):
        if cls.__init__ is not FrazzlBuilder.__init__:
            raise BuilderError(
                f"{cls.__name__} defined it's own __init__ function. Use the {cls.__name__}.build() method instead.")
        super().__init_subclass__(**kwargs)
        cls.build = Build(cls)

    @classmethod
    def build(cls, context):
        raise NotImplementedError

    @classmethod
    def validate(cls, definition):
        raise NotImplementedError
