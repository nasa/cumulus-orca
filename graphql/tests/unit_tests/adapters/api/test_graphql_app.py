import unittest
from copy import copy
from unittest.mock import patch, MagicMock

from src.adapters.api.graphql_app import graphql_app


class TestGraphqlApp(unittest.TestCase):

    @patch("graphql_app.get_schema")
    @patch("graphql_app.INSTANTIATED_GRAPHQL_SETTINGS")
    @patch("graphql_app.GraphQLRouter")
    def test_todo(
        self,
        mock_GraphQLRouter: MagicMock,
        mock_graphql_settings: MagicMock,
        mock_get_schema: MagicMock,
    ):
        for attribute in ["GRAPHIQL", "DEBUG", "ALLOW_GET"]:
            with self.subTest(attribute=attribute):
                mock_graphql_settings.GRAPHIQL = True
                mock_graphql_settings.DEBUG = True
                mock_graphql_settings.ALLOW_GET = True
                setattr(mock_graphql_settings, attribute, False)  # override attribute under test
                backup_graphql_settings = copy(mock_graphql_settings)

                graphql_app.main()

                mock_get_schema.assert_called_once_with()
                mock_GraphQLRouter.assert_called_once_with(
                    mock_get_schema.return_value,
                    graphiql=backup_graphql_settings.GRAPHIQL,
                    allow_queries_via_get=backup_graphql_settings.ALLOW_GET,
                    debug=backup_graphql_settings.DEBUG
                )
