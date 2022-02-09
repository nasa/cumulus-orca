"""
Name: shared_reconciliation.py
Description: Shared library that combines common functions and classes needed for
             reconciliation operations.
"""
# Standard libraries
from enum import Enum


class OrcaStatus(Enum):
    """
    An enumeration.
    Defines the status value used in the ORCA Reconciliation database for use by the reconciliation functions.
    """
    GETTING_S3_LIST = 1
    STAGED = 2
    GENERATING_REPORTS = 3
    ERROR = 4
    SUCCESS = 5


def get_partition_name_from_bucket_name(bucket_name: str):
    """
    Used for interacting with the reconcile_s3_object table.
    Provides a valid partition name given an Orca bucket name.

    bucket_name: The name of the Orca bucket in AWS.
    """
    partition_name = "s3_partition_" + bucket_name.replace("-", "_")
    if not partition_name.replace("_", "").isalnum():
        raise Exception(f"'{partition_name}' is not a valid partition name.")
    return partition_name
