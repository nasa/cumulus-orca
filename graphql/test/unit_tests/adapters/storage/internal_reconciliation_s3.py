import unittest
import uuid

from src.adapters.storage.internal_reconciliation_s3 import AWSS3FileLocation


class TestAWSS3FileLocation(unittest.TestCase):
    def test_constructor(self):
        """
        Constructor should properly store parameters.
        """
        bucket_name = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()

        location = AWSS3FileLocation(bucket_name, key)

        self.assertEqual(location.bucket_name, bucket_name)
        self.assertEqual(location.key, key)
