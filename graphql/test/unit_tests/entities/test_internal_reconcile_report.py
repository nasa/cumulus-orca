import random
import unittest
import uuid

from orca_shared.reconciliation import OrcaStatus

from src.entities.internal_reconcile_report import (
    InternalReconcileReportCreationRecord,
    InternalReconcileReportCursor,
    Mismatch,
    Phantom,
    ReconciliationStatus,
)
from src.use_cases.helpers.edge_cursor import EdgeCursor


class TestInternalReconcileReport(unittest.TestCase):
    def test_ReconciliationStatus_matches_shared_enum(self):
        """
        Constructor should properly store parameters.
        """
        shared_values = [(e.value, e.name) for e in OrcaStatus]
        strawberry_values = [(e.value, e.name) for e in ReconciliationStatus]

        self.assertEqual(shared_values, strawberry_values)

    def test_InternalReconcileReportCursor_constructor(self):
        """
        Constructor should properly store parameters.
        """
        job_id = random.randint(0, 99999999999999)  # nosec

        cursor = InternalReconcileReportCursor(job_id)

        self.assertEqual(cursor.job_id, job_id)

    def test_InternalReconcileReportCreationRecord_constructor(self):
        """
        Constructor should properly store encrypted cursor.
        Cursor should be decryptable.
        """
        job_id = 954604896415

        record = InternalReconcileReportCreationRecord(InternalReconcileReportCursor(job_id))

        self.assertEqual("eyJqb2JfaWQiOiA5NTQ2MDQ4OTY0MTUuMH0=", record.cursor)
        cursor = EdgeCursor.decode_cursor(record.cursor, InternalReconcileReportCursor)
        self.assertEqual(InternalReconcileReportCursor(job_id), cursor)

    def test_phantom_constructor(
        self,
    ):
        """
        Constructor should properly store parameters.
        """
        job_id = random.randint(0, 10000)  # nosec
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        key_path = uuid.uuid4().__str__()
        orca_etag = uuid.uuid4().__str__()
        orca_last_update = random.randint(0, 10000)  # nosec
        orca_size_in_bytes = random.randint(0, 10000)  # nosec
        orca_storage_class = uuid.uuid4().__str__()

        result = Phantom(
            job_id,
            collection_id,
            granule_id,
            filename,
            key_path,
            orca_etag,
            orca_last_update,
            orca_size_in_bytes,
            orca_storage_class,
        )

        # todo: Find a way to loop over properties and check them
        self.assertEqual(job_id, result.job_id)
        self.assertEqual(collection_id, result.collection_id)
        self.assertEqual(granule_id, result.granule_id)
        self.assertEqual(filename, result.filename)
        self.assertEqual(key_path, result.key_path)
        self.assertEqual(orca_etag, result.orca_etag)
        self.assertEqual(orca_last_update, result.orca_granule_last_update)
        self.assertEqual(orca_size_in_bytes, result.orca_size_in_bytes)
        self.assertEqual(orca_storage_class, result.orca_storage_class)

    def test_phantom_get_cursor(self):
        """
        get_cursor should return information that identifies an individual row.
        """
        job_id = random.randint(0, 10000)  # nosec
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        key_path = uuid.uuid4().__str__()
        orca_etag = uuid.uuid4().__str__()
        orca_last_update = random.randint(0, 10000)  # nosec
        orca_size_in_bytes = random.randint(0, 10000)  # nosec
        orca_storage_class = uuid.uuid4().__str__()

        result = Phantom(
            job_id,
            collection_id,
            granule_id,
            filename,
            key_path,
            orca_etag,
            orca_last_update,
            orca_size_in_bytes,
            orca_storage_class,
        ).get_cursor()

        # todo: Find a way to loop over properties and check them
        self.assertEqual(job_id, result.job_id)
        self.assertEqual(collection_id, result.collection_id)
        self.assertEqual(granule_id, result.granule_id)
        self.assertEqual(key_path, result.key_path)

    def test_mismatch_constructor(
        self,
    ):
        """
        Constructor should properly store parameters.
        """
        job_id = random.randint(0, 10000)  # nosec
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        key_path = uuid.uuid4().__str__()
        cumulus_archive_location = uuid.uuid4().__str__()
        orca_etag = uuid.uuid4().__str__()
        s3_etag = uuid.uuid4().__str__()
        orca_last_update = random.randint(0, 10000)  # nosec
        s3_last_update = random.randint(0, 10000)  # nosec
        orca_size_in_bytes = random.randint(0, 10000)  # nosec
        s3_size_in_bytes = random.randint(0, 10000)  # nosec
        orca_storage_class = uuid.uuid4().__str__()
        s3_storage_class = uuid.uuid4().__str__()
        discrepancy_type = uuid.uuid4().__str__()
        comment = uuid.uuid4().__str__()

        result = Mismatch(
            job_id,
            collection_id,
            granule_id,
            filename,
            key_path,
            cumulus_archive_location,
            orca_etag,
            s3_etag,
            orca_last_update,
            s3_last_update,
            orca_size_in_bytes,
            s3_size_in_bytes,
            orca_storage_class,
            s3_storage_class,
            discrepancy_type,
            comment,
        )

        # todo: Find a way to loop over properties and check them
        self.assertEqual(job_id, result.job_id)
        self.assertEqual(collection_id, result.collection_id)
        self.assertEqual(granule_id, result.granule_id)
        self.assertEqual(filename, result.filename)
        self.assertEqual(key_path, result.key_path)
        self.assertEqual(cumulus_archive_location, result.cumulus_archive_location)
        self.assertEqual(orca_etag, result.orca_etag)
        self.assertEqual(s3_etag, result.s3_etag)
        self.assertEqual(orca_last_update, result.orca_granule_last_update)
        self.assertEqual(s3_last_update, result.s3_file_last_update)
        self.assertEqual(orca_size_in_bytes, result.orca_size_in_bytes)
        self.assertEqual(s3_size_in_bytes, result.s3_size_in_bytes)
        self.assertEqual(orca_storage_class, result.orca_storage_class)
        self.assertEqual(s3_storage_class, result.s3_storage_class)
        self.assertEqual(discrepancy_type, result.discrepancy_type)
        self.assertEqual(comment, result.comment)

    def test_mismatch_get_cursor(self):
        """
        get_cursor should return information that identifies an individual row.
        """
        job_id = random.randint(0, 10000)  # nosec
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        key_path = uuid.uuid4().__str__()
        cumulus_archive_location = uuid.uuid4().__str__()
        orca_etag = uuid.uuid4().__str__()
        s3_etag = uuid.uuid4().__str__()
        orca_last_update = random.randint(0, 10000)  # nosec
        s3_last_update = random.randint(0, 10000)  # nosec
        orca_size_in_bytes = random.randint(0, 10000)  # nosec
        s3_size_in_bytes = random.randint(0, 10000)  # nosec
        orca_storage_class = uuid.uuid4().__str__()
        s3_storage_class = uuid.uuid4().__str__()
        discrepancy_type = uuid.uuid4().__str__()
        comment = uuid.uuid4().__str__()

        result = Mismatch(
            job_id,
            collection_id,
            granule_id,
            filename,
            key_path,
            cumulus_archive_location,
            orca_etag,
            s3_etag,
            orca_last_update,
            s3_last_update,
            orca_size_in_bytes,
            s3_size_in_bytes,
            orca_storage_class,
            s3_storage_class,
            discrepancy_type,
            comment,
        ).get_cursor()

        # todo: Find a way to loop over properties and check them
        self.assertEqual(job_id, result.job_id)
        self.assertEqual(collection_id, result.collection_id)
        self.assertEqual(granule_id, result.granule_id)
        self.assertEqual(key_path, result.key_path)
