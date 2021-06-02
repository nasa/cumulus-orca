"""
Name: test_post_to_database.py

Description:  Unit tests for test_post_to_database.py.
"""
import datetime
import json
import unittest
import uuid
from unittest.mock import Mock, call, patch, MagicMock

from fastjsonschema import JsonSchemaValueException

import post_to_database
from orca_shared.shared_recovery import OrcaStatus


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

    @patch('orca_shared.shared_db.get_user_connection')
    @patch('post_to_database.send_record_to_database')
    def test_task_happy_path(self,
                             mock_send_record_to_database: MagicMock,
                             mock_get_user_connection: MagicMock):
        record0 = Mock()
        record1 = Mock()
        records = [record0, record1]
        db_connect_info = Mock()
        mock_engine = Mock()
        mock_get_user_connection.return_value = mock_engine

        post_to_database.task(records, db_connect_info)

        mock_send_record_to_database.assert_has_calls([call(record0, mock_engine), call(record1, mock_engine)])
        self.assertEqual(2, mock_send_record_to_database.call_count)

    @patch('post_to_database.create_status_for_job_and_files')
    def test_send_record_to_database_create_status_for_job_and_files(self,
                                                                     mock_create_status_for_job_and_files: MagicMock):
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        request_time = datetime.datetime.utcnow().isoformat().__str__()
        archive_destination = uuid.uuid4().__str__()
        files = [{
            'filename': uuid.uuid4().__str__(), 'key_path': uuid.uuid4().__str__(),
            'restore_destination': uuid.uuid4().__str__(), 'status_id': 1,
            'request_time': datetime.datetime.utcnow().isoformat(),
            'last_update': datetime.datetime.utcnow().isoformat()
        }]

        values = {
            "job_id": job_id,
            "granule_id": granule_id,
            "request_time": request_time,
            "archive_destination": archive_destination,
            "files": files
        }
        request_method = post_to_database.RequestMethod.NEW_JOB
        mock_engine = Mock()
        record = {
            'body': json.dumps(values, indent=4),
            'messageAttributes': {'RequestMethod': request_method.value.__str__()}
        }

        post_to_database.send_record_to_database(record, mock_engine)

        mock_create_status_for_job_and_files.assert_called_once_with(job_id, granule_id, request_time,
                                                                     archive_destination, files, mock_engine)

    def test_send_record_to_database_create_status_for_job_and_files_errors_for_missing_properties(
            self):
        """
        No missing properties should be allowed
        """
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        request_time = datetime.datetime.utcnow().isoformat().__str__()
        archive_destination = uuid.uuid4().__str__()
        files = [{
            'filename': uuid.uuid4().__str__(), 'key_path': uuid.uuid4().__str__(),
            'restore_destination': uuid.uuid4().__str__(), 'status_id': 1,
            'request_time': datetime.datetime.utcnow().isoformat(),
            'last_update': datetime.datetime.utcnow().isoformat()
        }]
        values = {
            "job_id": job_id,
            "granule_id": granule_id,
            "request_time": request_time,
            "archive_destination": archive_destination,
            "files": files
        }
        request_method = post_to_database.RequestMethod.NEW_JOB
        mock_engine = Mock()

        for key in values.keys():
            input_values = values.copy()
            input_values.pop(key)
            record = {
                'body': json.dumps(input_values, indent=4),
                'messageAttributes': {'RequestMethod': request_method.value.__str__()}
            }
            schema_error_raised = False
            try:
                post_to_database.send_record_to_database(record, mock_engine)
            except JsonSchemaValueException:
                schema_error_raised = True

            if not schema_error_raised:
                self.fail(f"Key '{key}' schema_error_raised was '{schema_error_raised}'.")

    @patch('post_to_database.update_status_for_file')
    def test_send_record_to_database_update_status_for_file(self,
                                                            mock_update_status_for_file: MagicMock):
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        last_update = datetime.datetime.utcnow().isoformat().__str__()
        completion_time = datetime.datetime.utcnow().isoformat().__str__()
        status_id = 2
        error_message = uuid.uuid4().__str__()
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
        mock_engine = Mock()
        record = {
            'body': json.dumps(values, indent=4),
            'messageAttributes': {'RequestMethod': request_method.value.__str__()}
        }

        post_to_database.send_record_to_database(record, mock_engine)

        mock_update_status_for_file.assert_called_once_with(job_id, granule_id, filename, last_update, completion_time,
                                                            status_id, error_message, mock_engine)

    @patch('post_to_database.update_status_for_file')
    def test_send_record_to_database_update_status_for_file_defaults_for_missing_properties(
            self,
            mock_update_status_for_file: MagicMock):
        """
        Missing completion time and error_message are fine.
        """
        expected_defaults = {'completion_time': None, 'error_message': None}

        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        last_update = datetime.datetime.utcnow().isoformat().__str__()
        status_id = 3
        completion_time = datetime.datetime.utcnow().isoformat().__str__()
        error_message = uuid.uuid4().__str__()
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
        mock_engine = Mock()

        for key in values.keys():
            input_values = values.copy()
            input_values.pop(key)
            record = {
                'body': json.dumps(input_values, indent=4),
                'messageAttributes': {'RequestMethod': request_method.value.__str__()}
            }
            schema_error_raised = False
            try:
                post_to_database.send_record_to_database(record, mock_engine)
            except JsonSchemaValueException:
                schema_error_raised = True

            if schema_error_raised == expected_defaults.keys().__contains__(key):
                self.fail(f"Key '{key}' schema_error_raised was '{schema_error_raised}'.")
            if expected_defaults.keys().__contains__(key):
                expected_values = values.copy()
                # noinspection PyTypeChecker
                expected_values[key] = expected_defaults[key]
                expected_values['engine'] = mock_engine
                mock_update_status_for_file.assert_has_calls([call(expected_values['job_id'],
                                                                   expected_values['granule_id'],
                                                                   expected_values['filename'],
                                                                   expected_values['last_update'],
                                                                   expected_values['completion_time'],
                                                                   expected_values['status_id'],
                                                                   expected_values['error_message'], mock_engine)])

    @patch('post_to_database.create_file_sql')
    @patch('post_to_database.create_job_sql')
    def test_create_status_for_job_and_files_happy_path(self,
                                                        mock_create_job_sql: MagicMock,
                                                        mock_create_file_sql: MagicMock):
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        request_time = uuid.uuid4().__str__()
        archive_destination = uuid.uuid4().__str__()

        filename0 = uuid.uuid4().__str__()
        key_path0 = uuid.uuid4().__str__()
        restore_destination0 = uuid.uuid4().__str__()
        request_time0 = uuid.uuid4().__str__()
        last_update0 = uuid.uuid4().__str__()
        filename1 = uuid.uuid4().__str__()
        key_path1 = uuid.uuid4().__str__()
        restore_destination1 = uuid.uuid4().__str__()
        request_time1 = uuid.uuid4().__str__()
        last_update1 = uuid.uuid4().__str__()
        error_message1 = uuid.uuid4().__str__()
        completion_time1 = datetime.datetime.utcnow().isoformat()
        files = [
            {
                'status_id': OrcaStatus.PENDING.value,
                'filename': filename0,
                'key_path': key_path0,
                'restore_destination': restore_destination0,
                'request_time': request_time0,
                'last_update': last_update0
            },
            {
                'status_id': OrcaStatus.FAILED.value,
                'filename': filename1,
                'key_path': key_path1,
                'restore_destination': restore_destination1,
                'request_time': request_time1,
                'last_update': last_update1,
                'error_message': error_message1,
                'completion_time': completion_time1
            }
        ]

        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock()

        post_to_database.create_status_for_job_and_files(job_id, granule_id, request_time, archive_destination, files,
                                                         mock_engine)

        mock_connection.execute.assert_has_calls([
            call(
                mock_create_job_sql.return_value,
                [{'job_id': job_id, 'granule_id': granule_id, 'status_id': OrcaStatus.PENDING.value,
                  'request_time': request_time, 'completion_time': None,
                  'archive_destination': archive_destination}]
            ),
            call(
                mock_create_file_sql.return_value,
                [
                    {
                        'job_id': job_id, 'granule_id': granule_id, 'filename': filename0,
                        'key_path': key_path0, 'restore_destination': restore_destination0,
                        'status_id': OrcaStatus.PENDING.value, 'error_message': None,
                        'request_time': request_time0, 'last_update': last_update0,
                        'completion_time': None
                    },
                    {
                        'job_id': job_id, 'granule_id': granule_id, 'filename': filename1,
                        'key_path': key_path1, 'restore_destination': restore_destination1,
                        'status_id': OrcaStatus.FAILED.value, 'error_message': error_message1,
                        'request_time': request_time1, 'last_update': last_update1,
                        'completion_time': completion_time1
                    }]
            )
        ])
        self.assertEqual(2, mock_connection.execute.call_count)

    @patch('post_to_database.create_file_sql')
    @patch('post_to_database.create_job_sql')
    def test_create_status_for_job_and_files_all_files_failed(self,
                                                              mock_create_job_sql: MagicMock,
                                                              mock_create_file_sql: MagicMock
                                                              ):
        """
        If all files failed, job should be marked as such.
        """
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        request_time = uuid.uuid4().__str__()
        archive_destination = uuid.uuid4().__str__()

        filename0 = uuid.uuid4().__str__()
        key_path0 = uuid.uuid4().__str__()
        restore_destination0 = uuid.uuid4().__str__()
        request_time0 = uuid.uuid4().__str__()
        last_update0 = uuid.uuid4().__str__()
        error_message0 = uuid.uuid4().__str__()
        completion_time0 = datetime.datetime.utcnow().isoformat()
        filename1 = uuid.uuid4().__str__()
        key_path1 = uuid.uuid4().__str__()
        restore_destination1 = uuid.uuid4().__str__()
        request_time1 = uuid.uuid4().__str__()
        last_update1 = uuid.uuid4().__str__()
        error_message1 = uuid.uuid4().__str__()
        completion_time1 = datetime.datetime.utcnow().isoformat()
        # using a third item to make sure that all branches of file loop are hit
        filename2 = uuid.uuid4().__str__()
        key_path2 = uuid.uuid4().__str__()
        restore_destination2 = uuid.uuid4().__str__()
        request_time2 = uuid.uuid4().__str__()
        last_update2 = uuid.uuid4().__str__()
        error_message2 = uuid.uuid4().__str__()
        completion_time2 = datetime.datetime.utcnow().isoformat()
        files = [
            {
                'status_id': OrcaStatus.FAILED.value,
                'filename': filename0,
                'key_path': key_path0,
                'restore_destination': restore_destination0,
                'request_time': request_time0,
                'last_update': last_update0,
                'error_message': error_message0,
                'completion_time': completion_time0
            },
            {
                'status_id': OrcaStatus.FAILED.value,
                'filename': filename1,
                'key_path': key_path1,
                'restore_destination': restore_destination1,
                'request_time': request_time1,
                'last_update': last_update1,
                'error_message': error_message1,
                'completion_time': completion_time1
            },
            {
                'status_id': OrcaStatus.FAILED.value,
                'filename': filename2,
                'key_path': key_path2,
                'restore_destination': restore_destination2,
                'request_time': request_time2,
                'last_update': last_update2,
                'error_message': error_message2,
                'completion_time': completion_time2
            }
        ]

        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock()

        post_to_database.create_status_for_job_and_files(job_id, granule_id, request_time, archive_destination, files,
                                                         mock_engine)

        mock_connection.execute.assert_has_calls([
            call(
                mock_create_job_sql.return_value,
                [{'job_id': job_id, 'granule_id': granule_id, 'status_id': OrcaStatus.FAILED.value,
                  'request_time': request_time, 'completion_time': completion_time2.__str__(),
                  'archive_destination': archive_destination}]
            ),
            call(
                mock_create_file_sql.return_value,
                [
                    {
                        'job_id': job_id, 'granule_id': granule_id, 'filename': filename0,
                        'key_path': key_path0, 'restore_destination': restore_destination0,
                        'status_id': OrcaStatus.FAILED.value, 'error_message': error_message0,
                        'request_time': request_time0, 'last_update': last_update0,
                        'completion_time': completion_time0
                    },
                    {
                        'job_id': job_id, 'granule_id': granule_id, 'filename': filename1,
                        'key_path': key_path1, 'restore_destination': restore_destination1,
                        'status_id': OrcaStatus.FAILED.value, 'error_message': error_message1,
                        'request_time': request_time1, 'last_update': last_update1,
                        'completion_time': completion_time1
                    },
                    {
                        'job_id': job_id, 'granule_id': granule_id, 'filename': filename2,
                        'key_path': key_path2, 'restore_destination': restore_destination2,
                        'status_id': OrcaStatus.FAILED.value, 'error_message': error_message2,
                        'request_time': request_time2, 'last_update': last_update2,
                        'completion_time': completion_time2
                    }
                ]
            )
        ])
        self.assertEqual(2, mock_connection.execute.call_count)

    def test_create_status_for_job_and_files_bad_status_id(self):
        """
        Only 'PENDING' and 'FAILED' should be allowed on initial creation.
        """
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        request_time = uuid.uuid4().__str__()
        archive_destination = uuid.uuid4().__str__()

        filename0 = uuid.uuid4().__str__()
        key_path0 = uuid.uuid4().__str__()
        restore_destination0 = uuid.uuid4().__str__()
        request_time0 = uuid.uuid4().__str__()
        last_update0 = uuid.uuid4().__str__()
        error_message0 = uuid.uuid4().__str__()
        completion_time0 = datetime.datetime.utcnow().isoformat()

        for status in OrcaStatus:
            if status == OrcaStatus.FAILED or status == OrcaStatus.PENDING:
                continue
            files = [
                {
                    'status_id': OrcaStatus.STAGED.value,
                    'filename': filename0,
                    'key_path': key_path0,
                    'restore_destination': restore_destination0,
                    'request_time': request_time0,
                    'last_update': last_update0,
                    'error_message': error_message0,
                    'completion_time': completion_time0
                }
            ]

            with self.assertRaises(ValueError):
                post_to_database.create_status_for_job_and_files(job_id, granule_id, request_time, archive_destination,
                                                                 files, Mock())

    @patch('post_to_database.update_file_sql')
    @patch('post_to_database.update_job_sql')
    def test_update_status_for_file_happy_path(self,
                                               mock_update_job_sql: MagicMock,
                                               mock_update_file_sql: MagicMock
                                               ):
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        last_update = uuid.uuid4().__str__()
        completion_time = uuid.uuid4().__str__()
        status_id = 4
        error_message = uuid.uuid4().__str__()

        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock()

        post_to_database.update_status_for_file(job_id, granule_id, filename, last_update, completion_time, status_id,
                                                error_message, mock_engine)
        mock_connection.execute.assert_has_calls([
            call(
                mock_update_file_sql.return_value,
                {'status_id': status_id, 'last_update': last_update, 'completion_time': completion_time,
                 'error_message': error_message, 'job_id': job_id, 'granule_id': granule_id,
                 'filename': filename}
            ),
            call(
                mock_update_job_sql.return_value,
                {'job_id': job_id, 'granule_id': granule_id}
            )
        ])
        self.assertEqual(2, mock_connection.execute.call_count)
