import unittest
from unittest.mock import MagicMock, patch, Mock

from graphql import NoSchemaIntrospectionCustomRule

from src.adapters.graphql.schemas.schemas import get_schema


class TestSchemas(unittest.TestCase):

    @patch("src.adapters.graphql.schemas.schemas.AddValidationRules")
    @patch("src.adapters.graphql.schemas.schemas.Schema")
    @patch("src.adapters.graphql.schemas.schemas.Queries")
    def test_get_schema_happy_path(
        self,
        mock_queries: MagicMock,
        mock_schema: MagicMock,
        mock_add_validation_rules: MagicMock,
    ):
        """
        Should store adapters in static Queries property and initialize schema.
        """
        for graphiql_setting in [True, False]:
            with self.subTest(graphiql_setting=graphiql_setting):
                mock_graphql_settings = Mock()
                mock_graphql_settings.GRAPHIQL = graphiql_setting
                mock_adapters_storage = Mock()

                result = get_schema(mock_graphql_settings, mock_adapters_storage)

                self.assertEqual(mock_adapters_storage, mock_queries.adapters_storage)

                if not graphiql_setting:  # We only add this rule if graphiql access is denied.
                    mock_add_validation_rules.assert_called_once_with(
                        [NoSchemaIntrospectionCustomRule])
                else:
                    mock_add_validation_rules.assert_not_called()
                self.assertEqual(mock_schema.return_value, result)
                mock_schema.assert_called_once_with(
                    query=mock_queries,
                    extensions=
                    [mock_add_validation_rules.return_value, ]
                    if graphiql_setting is False else
                    []
                )

            mock_queries.reset_mock()
            mock_schema.reset_mock()
            mock_add_validation_rules.reset_mock()
