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
