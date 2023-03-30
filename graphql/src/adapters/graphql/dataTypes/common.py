import traceback

# noinspection PyPackageRequirements
import strawberry


# alternate error logic approaches:
# https://productionreadygraphql.com/2020-08-01-guide-to-graphql-errors
@strawberry.interface
class ErrorGraphqlTypeInterface:
    message: str


@strawberry.type
class InternalServerErrorGraphqlType(ErrorGraphqlTypeInterface):
    exception_message: str
    stack_trace: str

    def __init__(self, ex: Exception):
        self.message = "An unexpected error has occurred. " \
                       "Please review the logs and contact support if needed."
        self.exception_message = str(ex)
        self.stack_trace = traceback.format_exc()


# noinspection PyPep8Naming
class int8(int):
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return int8_parse_value(v)

    def __repr__(self):
        return f'PostCode({super().__repr__()})'


strawberry_int8 = strawberry.scalar(
    int8,
    serialize=lambda v: int8_serialize(v),
    parse_value=lambda v: int8_parse_value(v),
)

int8_max = 9223372036854775807
int8_min = int8_max * -1


def int8_serialize(v):
    if v > int8_max or v < int8_min:
        raise ValueError(f"Value {v} outside bounds of '{int8_min}' - '{int8_max}'.")
    return v


def int8_parse_value(v):
    val = int(v)
    if val > int8_max or val < int8_min:
        raise ValueError(f"Value {v} outside bounds of '{int8_min}' - '{int8_max}'.")
    return val
