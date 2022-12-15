import unittest
from unittest.mock import Mock, MagicMock, patch

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType


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
