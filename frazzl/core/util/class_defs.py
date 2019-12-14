def call_supers(obj_func, wrapper):
    return wrapper(obj_func)


def validate_class(cls):
    cls.validate = call_supers(cls.validate, validate)
    cls.context = {}
    return cls


def validate(func):
    def _validate(cls, definition):
        if object not in cls.__bases__:
            for parent_type in cls.__bases__:
                parent_validate_result = parent_type.validate(definition)
                cls.context.update(parent_validate_result)
        validate_result = func(definition)
        cls.context.update(validate_result)
        return cls.context

    return classmethod(_validate)
