from ariadne import ScalarType

_Any = ScalarType("_Any")


@_Any.value_parser
def parse_any(value):
    return value


_FieldSet = ScalarType("_FieldSet")


@_FieldSet.literal_parser
def parse_fieldset(value):
    return value.value
