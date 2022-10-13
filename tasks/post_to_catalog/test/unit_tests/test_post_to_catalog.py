"""
Name: test_post_to_catalog.py

Description:  Unit tests for test_post_to_catalog.py.
"""
import copy
import json
import os
import random
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, call, patch

import fastjsonschema

import post_to_catalog


class TestPostToDatabase(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestPostToDatabase.
    """

    @patch("post_to_catalog.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_happy_path(
        self,
        mock_get_configuration: MagicMock,
        mock_task: MagicMock,
    ):
        """
        Should call Task with records and db info.
        """
        records = Mock()
        event = {"Records": records}
        context = Mock()
        post_to_catalog.handler(event, context)
        mock_task.assert_called_once_with(records, mock_get_configuration.return_value)

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("post_to_catalog.send_record_to_database")
    def test_task_happy_path(
        self,
        mock_send_record_to_database: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        Should split records and call underlying function with each record.
        """
        record0 = Mock()
        record1 = Mock()
        records = [record0, record1]
        db_connect_info = Mock()
        mock_engine = Mock()
        mock_get_user_connection.return_value = mock_engine

        post_to_catalog.task(records, db_connect_info)

        mock_send_record_to_database.assert_has_calls(
            [call(record0, mock_engine), call(record1, mock_engine)]
        )
        self.assertEqual(2, mock_send_record_to_database.call_count)

    @patch("post_to_catalog.create_catalog_records")
    def test_send_record_to_database_happy_path(
        self, mock_create_catalog_records: MagicMock
    ):
        """
        Should accept a valid record and call underlying function with record's contained data.
        """
        provider = {
            "providerId": uuid.uuid4().__str__(),
            "name": None,
        }
        collection = {
            "collectionId": uuid.uuid4().__str__(),
            "shortname": uuid.uuid4().__str__(),
            "version": uuid.uuid4().__str__(),
        }
        granule = {
            "cumulusGranuleId": uuid.uuid4().__str__(),
            "cumulusCreateTime": datetime.now(timezone.utc).isoformat(),
            "executionId": uuid.uuid4().__str__(),
            "ingestTime": datetime.now(timezone.utc).isoformat(),
            "lastUpdate": datetime.now(timezone.utc).isoformat(),
            "files": [
                {
                    "name": uuid.uuid4().__str__(),
                    "cumulusArchiveLocation": uuid.uuid4().__str__(),
                    "orcaArchiveLocation": uuid.uuid4().__str__(),
                    "keyPath": uuid.uuid4().__str__(),
                    "sizeInBytes": random.randint(0, 10000),  # nosec
                    "hash": uuid.uuid4().__str__(),
                    "hashType": uuid.uuid4().__str__(),
                    "storageClass": "GLACIER",
                    "version": uuid.uuid4().__str__(),
                    "ingestTime": datetime.now(timezone.utc).isoformat(),
                    "etag": uuid.uuid4().__str__(),
                },
                {
                    "name": uuid.uuid4().__str__(),
                    "cumulusArchiveLocation": uuid.uuid4().__str__(),
                    "orcaArchiveLocation": uuid.uuid4().__str__(),
                    "keyPath": uuid.uuid4().__str__(),
                    "sizeInBytes": random.randint(0, 10000),  # nosec
                    "hash": None,
                    "hashType": None,
                    "storageClass": "DEEP_ARCHIVE",
                    "version": uuid.uuid4().__str__(),
                    "ingestTime": datetime.now(timezone.utc).isoformat(),
                    "etag": "etag1",
                },
            ],
        }

        mock_engine = Mock()
        record = {
            "body": json.dumps(
                {"provider": provider, "collection": collection, "granule": granule},
                indent=4,
            )
        }

        post_to_catalog.send_record_to_database(record, mock_engine)

        mock_create_catalog_records.assert_called_once_with(
            provider, collection, granule, mock_engine
        )

    @patch("post_to_catalog.create_catalog_records")
    def test_send_record_to_database_rejects_bad_record(
        self, mock_create_catalog_records: MagicMock
    ):
        """
        Anything that doesn't match the schema should be rejected with an error.
        """
        provider = {
            #  "providerId": uuid.uuid4().__str__(),
            "name": uuid.uuid4().__str__()
        }
        collection = {
            "collectionId": uuid.uuid4().__str__(),
            "shortname": uuid.uuid4().__str__(),
            "version": uuid.uuid4().__str__(),
        }
        granule = {
            "cumulusGranuleId": uuid.uuid4().__str__(),
            "cumulusCreateTime": datetime.now(timezone.utc).isoformat(),
            "executionId": uuid.uuid4().__str__(),
            "ingestTime": datetime.now(timezone.utc).isoformat(),
            "lastUpdate": datetime.now(timezone.utc).isoformat(),
            "files": [],
        }

        mock_engine = Mock()
        record = {
            "body": json.dumps(
                {"provider": provider, "collection": collection, "granule": granule},
                indent=4,
            )
        }

        with self.assertRaises(fastjsonschema.exceptions.JsonSchemaValueException):
            post_to_catalog.send_record_to_database(record, mock_engine)

        mock_create_catalog_records.assert_not_called()

    @patch("post_to_catalog.create_file_sql")
    @patch("post_to_catalog.create_granule_sql")
    @patch("post_to_catalog.create_collection_sql")
    @patch("post_to_catalog.create_provider_sql")
    def test_create_catalog_records_happy_path(
        self,
        mock_create_provider_sql: MagicMock,
        mock_create_collection_sql: MagicMock,
        mock_create_granule_sql: MagicMock,
        mock_create_file_sql: MagicMock,
    ):
        """
        Should perform several SQL operations with separated files.
        """
        provider = {
            "providerId": uuid.uuid4().__str__(),
            "name": uuid.uuid4().__str__(),
        }
        collection = {
            "collectionId": uuid.uuid4().__str__(),
            "shortname": uuid.uuid4().__str__(),
            "version": uuid.uuid4().__str__(),
        }
        file0 = {
            "name": uuid.uuid4().__str__(),
            "cumulusArchiveLocation": uuid.uuid4().__str__(),
            "orcaArchiveLocation": uuid.uuid4().__str__(),
            "keyPath": uuid.uuid4().__str__(),
            "sizeInBytes": random.randint(0, 10000),  # nosec
            "hash": uuid.uuid4().__str__(),
            "hashType": uuid.uuid4().__str__(),
            "storageClass": uuid.uuid4().__str__(),
            "version": uuid.uuid4().__str__(),
            "ingestTime": datetime.now(timezone.utc).isoformat(),
            "etag": uuid.uuid4().__str__(),
        }
        file1 = {
            "name": uuid.uuid4().__str__(),
            "cumulusArchiveLocation": uuid.uuid4().__str__(),
            "orcaArchiveLocation": uuid.uuid4().__str__(),
            "keyPath": uuid.uuid4().__str__(),
            "sizeInBytes": random.randint(0, 10000),  # nosec
            "hash": None,
            "hashType": None,
            "storageClass": uuid.uuid4().__str__(),
            "version": uuid.uuid4().__str__(),
            "ingestTime": datetime.now(timezone.utc).isoformat(),
            "etag": uuid.uuid4().__str__(),
        }
        granule = {
            "cumulusGranuleId": uuid.uuid4().__str__(),
            "cumulusCreateTime": datetime.now(timezone.utc).isoformat(),
            "executionId": uuid.uuid4().__str__(),
            "ingestTime": datetime.now(timezone.utc).isoformat(),
            "lastUpdate": datetime.now(timezone.utc).isoformat(),
            "files": [file0, file1],
        }

        internal_id = random.randint(0, 10000)  # nosec
        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_connection.execute.return_value = [{"id": internal_id}]
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock(return_value=False)

        post_to_catalog.create_catalog_records(
            copy.deepcopy(provider),
            copy.deepcopy(collection),
            copy.deepcopy(granule),
            mock_engine,
        )

        mock_connection.execute.assert_has_calls(
            [
                call(
                    mock_create_provider_sql.return_value,
                    [{"provider_id": provider["providerId"], "name": provider["name"]}],
                ),
                call(
                    mock_create_collection_sql.return_value,
                    [
                        {
                            "collection_id": collection["collectionId"],
                            "shortname": collection["shortname"],
                            "version": collection["version"],
                        }
                    ],
                ),
                call(
                    mock_create_granule_sql.return_value,
                    [
                        {
                            "provider_id": provider["providerId"],
                            "collection_id": collection["collectionId"],
                            "cumulus_granule_id": granule["cumulusGranuleId"],
                            "execution_id": granule["executionId"],
                            "ingest_time": granule["ingestTime"],
                            "cumulus_create_time": granule["cumulusCreateTime"],
                            "last_update": granule["lastUpdate"],
                        }
                    ],
                ),
                call(
                    mock_create_file_sql.return_value,
                    [
                        {
                            "granule_id": internal_id,
                            "name": file0["name"],
                            "cumulus_archive_location": file0["cumulusArchiveLocation"],
                            "orca_archive_location": file0["orcaArchiveLocation"],
                            "key_path": file0["keyPath"],
                            "size_in_bytes": file0["sizeInBytes"],
                            "hash": file0["hash"],
                            "hash_type": file0["hashType"],
                            "storage_class": file0["storageClass"],
                            "version": file0["version"],
                            "ingest_time": file0["ingestTime"],
                            "etag": file0["etag"],
                        },
                        {
                            "granule_id": internal_id,
                            "name": file1["name"],
                            "cumulus_archive_location": file1["cumulusArchiveLocation"],
                            "orca_archive_location": file1["orcaArchiveLocation"],
                            "key_path": file1["keyPath"],
                            "size_in_bytes": file1["sizeInBytes"],
                            "hash": None,  # None is a valid value.
                            "hash_type": None,
                            "storage_class": file1["storageClass"],
                            "version": file1["version"],
                            "ingest_time": file1["ingestTime"],
                            "etag": file1["etag"],
                        },
                    ],
                ),
            ]
        )
