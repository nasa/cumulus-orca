import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType, int8, \
    int8_min, int8_max, strawberry_int8


class TestCommon(unittest.TestCase):

    @patch("src.adapters.graphql.dataTypes.common.traceback")
    def test_InternalServerErrorGraphqlType_init_mapping(
        self,
        mock_traceback: MagicMock,
    ):
        """
        Constructor parameters should be stored properly.
        """
        mock_ex = Mock()

        result = InternalServerErrorGraphqlType(mock_ex)

        self.assertEqual(str(mock_ex), result.exception_message)
        mock_traceback.format_exc.assert_called_once_with()
        self.assertEqual(mock_traceback.format_exc.return_value, result.stack_trace)

    def test_int8_validate_happy_path(
        self
    ):
        """
        If value is in valid range, return as int-compatible value.
        """
        values = [-9223372036854775807, 0, 9223372036854775807]
        for value in values:
            with self.subTest(value=value):
                result = int8(value)
                int8.validate(value)
                self.assertEqual(value, result)

    def test_int8_validate_out_of_bounds_raises_error(
        self
    ):
        """
        If value is beyond bounds, raise error.
        """
        values = [-9223372036854775808, 9223372036854775808]
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as cm:
                    int8.validate(value)
                self.assertEqual(f"Value {value} outside bounds of '{int8_min}' - '{int8_max}'.",
                                 str(cm.exception))

    def test_int8_validate_non_numeric_raises_error(
        self
    ):
        """
        Non-numeric values should raise an error.
        """
        value = uuid.uuid4().__str__()
        with self.assertRaises(ValueError) as cm:
            int8.validate(value)
        self.assertEqual(f"invalid literal for int() with base 10: '{value}'",
                         str(cm.exception))

    def test_strawberry_int8(
        self
    ):
        """
        Ensure that strawberry_int8 implements int8
        """
        temp = strawberry_int8(5)
        self.assertIsInstance(temp, int8)

    # Parsing and serializing for strawberry scalars is automagical, and is not unit-testable.
