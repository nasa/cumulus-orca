import unittest
from unittest.mock import MagicMock, Mock, patch

from starlette.middleware.cors import CORSMiddleware

from src.adapters.api.fastapi import create_fastapi_app


class TestFastapi(unittest.TestCase):

    @patch("src.adapters.api.fastapi.GraphQLSettings")
    @patch("src.adapters.api.fastapi.get_graphql_app")
    @patch("src.adapters.api.fastapi.FastAPI")
    def test_create_fastapi_app_happy_path(
        self,
        mock_fast_api: MagicMock,
        mock_get_graphql_app: MagicMock,
        mock_graphql_settings: MagicMock,
    ):
        mock_uvicorn_settings = Mock()
        mock_adapters_storage = Mock()

        create_fastapi_app(mock_uvicorn_settings, mock_adapters_storage)

        mock_fast_api.assert_called_once_with()
        mock_app: MagicMock = mock_fast_api.return_value
        mock_app.add_middleware.assert_called_once_with(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        )
        mock_graphql_settings.assert_called_once_with(mock_uvicorn_settings)
        mock_get_graphql_app.assert_called_once_with(
            mock_graphql_settings.return_value, mock_adapters_storage)
        mock_app.include_router.assert_called_once_with(
            router=mock_get_graphql_app.return_value,
            prefix="/graphql"
        )
