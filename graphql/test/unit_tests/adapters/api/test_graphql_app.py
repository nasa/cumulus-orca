import unittest
from copy import copy
from unittest.mock import MagicMock, Mock, patch

from src.adapters.api.graphql_app import get_graphql_app


class TestGraphqlApp(unittest.TestCase):

    @patch("src.adapters.api.graphql_app.get_schema")
    @patch("src.adapters.api.graphql_app.GraphQLRouter")
    def test_get_graphql_app_happy_path(
        self,
        mock_GraphQLRouter: MagicMock,
        mock_get_schema: MagicMock,
    ):
        graphiql = Mock()
        debug = Mock()
        allow_get = Mock()
        mock_graphql_settings = Mock()
        mock_graphql_settings.GRAPHIQL = graphiql
        mock_graphql_settings.DEBUG = debug
        mock_graphql_settings.ALLOW_GET = allow_get
        mock_adapters_storage = Mock()

        get_graphql_app(mock_graphql_settings, mock_adapters_storage)

        mock_get_schema.assert_called_once_with(
            mock_graphql_settings, mock_adapters_storage)
        mock_GraphQLRouter.assert_called_once_with(
            mock_get_schema.return_value,
            graphiql=graphiql,
            allow_queries_via_get=allow_get,
            debug=debug
        )
