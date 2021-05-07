"""
Name: test_post_to_database.py

Description:  Unit tests for test_post_to_database.py.
"""
import json
import unittest
import uuid
from unittest.mock import Mock, call, patch, MagicMock

import post_to_database


class TestPostToDatabase(unittest.TestCase):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestPostToDatabase.
    """

    @patch('post_to_database.task')
    @patch('orca_shared.shared_db.get_configuration')
    @patch('cumulus_logger.CumulusLogger.setMetadata')
    def test_handler_happy_path(self,
                                mock_set_metadata: MagicMock,
                                mock_get_configuration: MagicMock,
                                mock_task: MagicMock):
        records = Mock()
        event = {'Records': records}
        context = Mock()
        post_to_database.handler(event, context)
        mock_set_metadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(records, mock_get_configuration.return_value)

    @patch('post_to_database.send_record_to_database')
    def test_task_happy_path(self,
                             mock_send_record_to_database: MagicMock):
        record0 = Mock()
        record1 = Mock()
        records = [record0, record1]
        db_connect_info = Mock()

        post_to_database.task(records, db_connect_info)

        mock_send_record_to_database.assert_has_calls([call(record0, db_connect_info), call(record1, db_connect_info)])
        self.assertEqual(2, mock_send_record_to_database.call_count)

    @patch('post_to_database.update_status_for_file')
    def test_send_record_to_database(self,
                                     mock_update_status_for_file: MagicMock):
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        last_update = uuid.uuid4().__str__()
        completion_time = uuid.uuid4().__str__()  # todo: Another test with missing
        status_id = uuid.uuid4().__str__()
        error_message = uuid.uuid4().__str__()  # todo: Another test with missing
        values = {
            "job_id": job_id,
            "granule_id": granule_id,
            "filename": filename,
            "last_update": last_update,
            "status_id": status_id,
            "completion_time": completion_time,
            "error_message": error_message
        }
        request_method = post_to_database.RequestMethod.UPDATE_FILE
        db_connect_info = Mock()
        record = {
            'body': json.dumps(values, indent=4),
            'messageAttributes': {'RequestMethod': request_method.value.__str__()}
        }

        post_to_database.send_record_to_database(record, db_connect_info)

        mock_update_status_for_file.assert_called_once_with(job_id, granule_id, filename, last_update, completion_time,
                                                            status_id, error_message, db_connect_info)

    @patch('post_to_database.update_row_in_table')
    def test_send_values_to_database_PUT_orca_recoverfile(self,
                                                          mock_update_row_in_table: MagicMock):
        """
        Use correct keys when updating a table.
        """
        table_name = 'orca_recoverfile'
        values = Mock()
        db_connect_info = Mock()

        post_to_database.send_values_to_database(table_name, values, post_to_database.RequestMethod.PUT,
                                                 db_connect_info)

        mock_update_row_in_table.assert_called_once_with(table_name, ['job_id', 'granule_id', 'filename'], values,
                                                         db_connect_info)

    @patch('post_to_database.update_row_in_table')
    def test_send_values_to_database_PUT_orca_recoveryjob(self,
                                                          mock_update_row_in_table: MagicMock):
        """
        Use correct keys when updating a table.
        """
        table_name = 'orca_recoveryjob'
        values = Mock()
        db_connect_info = Mock()

        post_to_database.send_values_to_database(table_name, values, post_to_database.RequestMethod.PUT,
                                                 db_connect_info)

        mock_update_row_in_table.assert_called_once_with(table_name, ['job_id', 'granule_id'], values,
                                                         db_connect_info)

    @patch('cumulus_logger.CumulusLogger.error')
    @patch('post_to_database.update_row_in_table')
    def test_send_values_to_database_PUT_error_logs(self,
                                                    mock_update_row_in_table: MagicMock,
                                                    mock_error: MagicMock):
        """
        Use correct keys when updating a table.
        """
        table_name = 'orca_recoverfile'
        values = Mock()
        db_connect_info = Mock()
        error = Exception()
        mock_update_row_in_table.side_effect = error

        post_to_database.send_values_to_database(table_name, values, post_to_database.RequestMethod.PUT,
                                                 db_connect_info)

        mock_update_row_in_table.assert_called_once_with(table_name, ['job_id', 'granule_id', 'filename'], values,
                                                         db_connect_info)
        mock_error.assert_called_once_with(error)

    @patch('cumulus_logger.CumulusLogger.error')
    @patch('post_to_database.update_row_in_table')
    def test_send_values_to_database_bad_table_logs(self,
                                                    mock_update_row_in_table: MagicMock,
                                                    mock_error: MagicMock):
        """
        If table doesn't have known keys, can't post.
        """
        table_name = uuid.uuid4().__str__()
        values = Mock()
        db_connect_info = Mock()

        post_to_database.send_values_to_database(table_name, values, post_to_database.RequestMethod.PUT,
                                                 db_connect_info)
        mock_update_row_in_table.assert_not_called()
        mock_error.assert_called_once()

    @patch('post_to_database.insert_row_from_values')
    def test_send_values_to_database_post_happy_path(self,
                                                     mock_insert_row_from_values: MagicMock):
        table_name = uuid.uuid4().__str__()
        values = Mock()
        db_connect_info = Mock()

        post_to_database.send_values_to_database(table_name, values, post_to_database.RequestMethod.POST,
                                                 db_connect_info)

        mock_insert_row_from_values.assert_called_once_with(table_name, values, db_connect_info)

    @patch('cumulus_logger.CumulusLogger.error')
    @patch('post_to_database.insert_row_from_values')
    def test_send_values_to_database_POST_error_logs(self,
                                                     mock_insert_row_from_values: MagicMock,
                                                     mock_error: MagicMock):
        """
        Use correct keys when updating a table.
        """
        table_name = uuid.uuid4().__str__()
        values = Mock()
        db_connect_info = Mock()
        error = Exception()
        mock_insert_row_from_values.side_effect = error

        post_to_database.send_values_to_database(table_name, values, post_to_database.RequestMethod.POST,
                                                 db_connect_info)

        mock_insert_row_from_values.assert_called_once_with(table_name, values, db_connect_info)
        mock_error.assert_called_once_with(error)

    @patch('database.single_query')
    def test_insert_row_from_values_happy_path(self,
                                               mock_single_query: MagicMock):
        table_name = uuid.uuid4().__str__()
        column0 = uuid.uuid4().__str__()
        value0 = uuid.uuid4().__str__()
        column1 = uuid.uuid4().__str__()
        value1 = uuid.uuid4().__str__()
        values = {column0: value0, column1: value1}
        db_connect_info = Mock()

        post_to_database.insert_row_from_values(table_name, values, db_connect_info)

        mock_single_query.assert_called_once_with(
            f"\n                    INSERT INTO {table_name} ({column0}, {column1})\n"
            f"                    VALUES (%s, %s)",
            db_connect_info, (value0, value1,))

    @patch('database.single_query')
    def test_update_row_in_table_happy_path(self,
                                            mock_single_query: MagicMock):
        table_name = uuid.uuid4().__str__()
        key0 = uuid.uuid4().__str__()
        key_value0 = uuid.uuid4().__str__()
        key1 = uuid.uuid4().__str__()
        key_value1 = uuid.uuid4().__str__()
        column0 = uuid.uuid4().__str__()
        value0 = uuid.uuid4().__str__()
        column1 = uuid.uuid4().__str__()
        value1 = uuid.uuid4().__str__()
        values = {key0: key_value0, key1: key_value1, column0: value0, column1: value1}
        db_connect_info = Mock()

        post_to_database.update_row_in_table(table_name, [key0, key1], values, db_connect_info)

        mock_single_query.assert_called_once_with(
            f"\n                    UPDATE {table_name}\n"
            f"                    SET {column0} = %s, {column1} = %s\n"
            f"                    WHERE {key0} = %s AND {key1} = %s",
            db_connect_info, (value0, value1, key_value0, key_value1))
