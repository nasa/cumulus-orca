"""
Name: test_db_deploy.py

Description:  Unit tests for db_deploy.py.
"""
import os
import unittest
import db_config
import db_deploy


class TestRequestStatus(unittest.TestCase):
    """
    TestRequestStatus.
    """
    def setUp(self):
        db_config.set_env()
        os.environ["PLATFORM"] = "ONPREM"
        os.environ["SCHEMA_DIR"] = "C:\\devpy\\poswotdr\\database\\ddl\\base\\"


    def tearDown(self):
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]
        del os.environ["PLATFORM"]


    def test_task_drop(self):
        """
        Test db_deploy task.
        """
        handler_input_event = {}
        expected = "database ddl execution complete"
        os.environ["DROP_DATABASE"] = "True"
        try:
            result = db_deploy.task(handler_input_event, None)
            self.assertEqual(expected, result)
        except Exception as err:
            self.fail(str(err))

    def test_task_no_drop(self):
        """
        Test db_deploy task.
        """
        handler_input_event = {}
        expected = "database ddl execution complete"
        os.environ["DROP_DATABASE"] = "False"
        try:
            result = db_deploy.task(handler_input_event, None)
            self.assertEqual(expected, result)
        except Exception as err:
            self.fail(str(err))

if __name__ == '__main__':
    unittest.main(argv=['start'])
