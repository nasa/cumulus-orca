import unittest
from copy import copy
from unittest.mock import patch, MagicMock, Mock

from src.adapters.api.graphql_app import get_graphql_app


class TestGraphqlApp(unittest.TestCase):

    @patch("src.adapters.api.graphql_app.get_schema")
    @patch("src.adapters.api.graphql_app.GraphQLRouter")
    def test_todo(
        self,
        mock_GraphQLRouter: MagicMock,
        mock_get_schema: MagicMock,
    ):
        for attribute in ["GRAPHIQL", "DEBUG", "ALLOW_GET"]:
            with self.subTest(attribute=attribute):
                mock_instantiated_graphql_settings = Mock()
                mock_instantiated_graphql_settings.GRAPHIQL = True
                mock_instantiated_graphql_settings.DEBUG = True
                mock_instantiated_graphql_settings.ALLOW_GET = True
                setattr(mock_instantiated_graphql_settings, attribute, False)  # override attribute under test
                backup_instantiated_graphql_settings = copy(mock_instantiated_graphql_settings)

                get_graphql_app(mock_instantiated_graphql_settings)

                mock_get_schema.assert_called_once_with(mock_instantiated_graphql_settings)
                mock_get_schema.reset_mock()
                mock_GraphQLRouter.assert_called_once_with(
                    mock_get_schema.return_value,
                    graphiql=backup_instantiated_graphql_settings.GRAPHIQL,
                    allow_queries_via_get=backup_instantiated_graphql_settings.ALLOW_GET,
                    debug=backup_instantiated_graphql_settings.DEBUG
                )
                mock_GraphQLRouter.reset_mock()
