import unittest
from unittest.mock import MagicMock, patch

from src.adapters.webserver.main import main


class TestApplication(unittest.TestCase):

    @patch("src.adapters.webserver.main.get_application")
    @patch("src.adapters.webserver.main.uvicorn")
    @patch("src.adapters.webserver.main.UvicornSettings")
    def test_main_happy_path(
        self,
        mock_uvicorn_settings: MagicMock,
        mock_uvicorn: MagicMock,
        mock_get_application: MagicMock,
    ):
        """
        Should run in uvicorn based on settings.
        """
        main()

        mock_uvicorn_settings.assert_called_once_with()
        mock_get_application.assert_called_once_with(mock_uvicorn_settings.return_value)
        mock_uvicorn.run.assert_called_once_with(
            app=mock_get_application.return_value,
            host=mock_uvicorn_settings.return_value.HOST,
            port=mock_uvicorn_settings.return_value.PORT,
            reload=False
        )
