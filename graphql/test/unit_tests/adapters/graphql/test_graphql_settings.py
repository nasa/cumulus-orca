import unittest
from unittest.mock import Mock

from src.adapters.graphql.graphql_settings import GraphQLSettings


class TestGraphqlSettings(unittest.TestCase):

    def test_init_happy_path(self):
        """
        Parameters should properly map to properties.
        """
        mock_webserver_settings = Mock()
        mock_webserver_settings.DEV = Mock(spec=bool)

        result = GraphQLSettings(mock_webserver_settings)
        self.assertEqual(result.GRAPHIQL, mock_webserver_settings.DEV)
        self.assertEqual(result.DEBUG, mock_webserver_settings.DEV)
        self.assertEqual(result.ALLOW_GET, mock_webserver_settings.DEV)
