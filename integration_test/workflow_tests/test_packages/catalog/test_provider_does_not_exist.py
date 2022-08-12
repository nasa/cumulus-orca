import json
import time
import uuid
from unittest import TestCase

import helpers


class TestProviderDoesNotExist(TestCase):
    def test_provider_does_not_exist_returns_empty_granules_list(self):
        """
        Presently, we do not raise an error if the providerId is not present in our catalog.
        """
        # Set up Orca API resources
        # ---
        my_session = helpers.create_session()

        catalog_output = helpers.post_to_api(
            my_session,
            helpers.api_url + "/catalog/reconcile/",
            data=json.dumps(
                {
                    "pageIndex": 0,
                    "providerId": [uuid.uuid4().__str__()],
                    "endTimestamp": int((time.time() + 5) * 1000),
                }
            ),
            headers={"Host": helpers.aws_api_name},
        )
        self.assertEqual(
            200, catalog_output.status_code, "Error occurred while contacting API."
        )
        self.assertEqual(
            {"granules": [], "anotherPage": False},
            catalog_output.json(),
            "Expected empty granule list not returned.",
        )
