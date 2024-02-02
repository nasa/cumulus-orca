import logging
import os
from unittest import TestCase, mock

from pydantic import ValidationError

from src.simple_input.schema import OverrideSettings
from src.simple_input.use_cases import get_settings


@mock.patch.dict(
    os.environ,
    {
        "DEFAULT_STORAGE_CLASS": "GLACIER",
        "DEFAULT_ORCA_BUCKET": "orca_primary_archive",
        "DEFAULT_MULTIPART_CHUNKSIZE_MB": "256",
    },
    clear=True,
)
class ConfigUseCase(TestCase):
    """
    Use cases related to setting the configuration
    and overrides form the environment and user provided
    information sent via the input event.
    """

    def test_env_settings_only_override_none(self):
        """
        Test that environment settings are only set.
        """
        logger = logging.getLogger("simple_input.use_cases")

        _test_env = get_settings(logger)

        self.assertEqual(_test_env.storage_class, "GLACIER")
        self.assertEqual(_test_env.excluded_files_regex, None)

    def test_env_override_values_all(self):
        """
        Test overrides of environment settings.
        """
        _env_overrides = OverrideSettings(
            defaultStorageClassOverride="DEEP_ARCHIVE", excludedFileExtensions=["*.xml"]
        )
        logger = logging.getLogger("simple_input.use_cases")

        _test_env = get_settings(logger, _env_overrides)

        self.assertEqual(_test_env.storage_class, "DEEP_ARCHIVE")
        self.assertEqual(_test_env.excluded_files_regex, ["*.xml"])

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_env_missing_required_env_variable(self):
        """
        Test that an unset environment with no user overrides
        throws an error.
        """
        logger = logging.getLogger("simple_input.use_cases")

        with self.assertRaises(ValidationError) as test_ex:
            _ = get_settings(logger)

        error_msg = """3 validation errors for DefaultSettings
DEFAULT_STORAGE_CLASS
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.6/v/missing
DEFAULT_ORCA_BUCKET
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.6/v/missing
DEFAULT_MULTIPART_CHUNKSIZE_MB
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.6/v/missing"""  # noqa: E501
        self.assertEqual(str(test_ex.exception), error_msg)

    def test_env_pass_null_override_value(self):
        """
        Testing logic to make sure if we pass a null or None
        value for an override we take the value in the DEFAULT
        environment.
        """
        _env_overrides = OverrideSettings(
            defaultStorageClassOverride=None, excludedFileExtensions=["*.xml"]
        )
        logger = logging.getLogger("simple_input.use_cases")

        _test_env = get_settings(logger, _env_overrides)

        self.assertEqual(_test_env.storage_class, "GLACIER")
        self.assertEqual(_test_env.excluded_files_regex, ["*.xml"])
