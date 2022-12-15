import os
import random
import unittest
import uuid
from unittest.mock import patch

from src.adapters.webserver.uvicorn_settings import UvicornSettings


class TestUvicornSettings(unittest.TestCase):

    def test_init_environ(self):
        """
        os.environ should be able to override values.
        """
        mock_host = uuid.uuid4().__str__()
        mock_port = random.randint(0, 99999)
        mock_db_connect_info = uuid.uuid4().__str__()

        for orca_env in ["production", "development", None, ""]:
            with self.subTest(orca_env=orca_env):
                with patch.dict(os.environ,
                                {
                                    "HOST": mock_host, "PORT": mock_port.__str__(),
                                    "ORCA_ENV": orca_env,
                                    "DB_CONNECT_INFO": mock_db_connect_info,
                                } if orca_env is not None else
                                {
                                    "HOST": mock_host, "PORT": mock_port.__str__(),
                                    "DB_CONNECT_INFO": mock_db_connect_info,
                                },
                                clear=True):
                    result = UvicornSettings()

                self.assertEqual(mock_host, result.HOST)
                self.assertEqual(mock_port, result.PORT)
                self.assertEqual(True if orca_env == "development" else False, result.DEV)
                self.assertEqual(mock_db_connect_info, result.DB_CONNECT_INFO)
