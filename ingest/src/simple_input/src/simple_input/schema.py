from typing import List

from pydantic import AliasChoices, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .entities import StorageTypes


class DefaultSettings(BaseSettings):
    """
    Default settings retrieved from the environment.
    Note that any non-null value passed in by the
    user can override these values.
    """

    model_config = SettingsConfigDict(case_sensitive=True)

    storage_class: StorageTypes = Field(
        alias=AliasChoices("DEFAULT_STORAGE_CLASS", "storage_class"),
        title="ORCA storage class",
        description="The default storage class used for storing the files.",
        json_schema_extra={
            "example": ["GLACIER", "DEEP_ARCHIVE"],
        },
    )
    orca_bucket: str = Field(
        alias=AliasChoices("DEFAULT_ORCA_BUCKET", "orca_bucket"),
        title="Default ORCA archiving bucket",
        description="Default ORCA storage bucket to use for backed up data.",
    )
    multipart_chunksize: int = Field(
        alias=AliasChoices("DEFAULT_MULTIPART_CHUNKSIZE_MB", "multipart_chunksize"),
        title="Multipart Chunk Size in Megabytes",
        description="The default multipart chunk size affects performance and copy time.",
    )
    excluded_files_regex: List[str] | None = Field(
        alias=AliasChoices("DEFAULT_EXCLUDED_FILES_REGEX", "excluded_files_regex"),
        default=None,
        title="List of regular expressions",
        description="Regular expressions that will exclude files from being backed up in ORCA.",
    )


class OverrideSettings(BaseModel):
    """
    Configuration items that allow for overrides and fine tuning
    of ingest of the data beyond default settings. This is provided
    by the user at time of ingest.
    """

    storage_class: StorageTypes | None = Field(
        default=None,
        alias="defaultStorageClassOverride",
        title="ORCA storage class over ride",
        description="Overrides the default storage class used for storing the files.",
        json_schema_extra={
            "example": ["GLACIER", "DEEP_ARCHIVE"],
        },
    )
    orca_bucket: str | None = Field(
        default=None,
        alias="defaultBucketOverride",
        title="Default ORCA archiving bucket",
        description="Default ORCA storage bucket to use for backed up data.",
    )
    multipart_chunksize: int | None = Field(
        default=None,
        alias="s3MultipartChunksizeMb",
        title="Multipart Chunk Size in Megabytes",
        description="The default multipart chunk size affects performance and copy time.",
    )
    excluded_files_regex: List[str] | None = Field(
        default=None,
        alias="excludedFileExtensions",
        title="List of regular expressions",
        description="Regular expressions that will exclude files from being backed up in ORCA.",
    )


class Input(BaseModel):
    """
    Client input schema
    """

    execution_id: str = Field(
        alias="executionId",
        title="Client execution ID",
        description="Execution ID of user process used for traceability between systems.",
        json_schema_extra={
            "example": [
                "arn:aws:states:us-west-2:23456789:execution:lp-GranWorkflow:ECO_L2T_002-6dff0ef9",
                "user-submitted:application:UUID4",
            ],
        },
    )
    configuration_overrides: OverrideSettings | None = Field(
        default=None,
        alias="configOverride",
        title="Configuration and settings overrides",
        description="Overrides the default configuration and environment settings.",
        json_schema_extra={
            "example": ["null", "{}"],
        },
    )
    data: str = Field(
        title="Message to send",
        description="Message for testing",
    )


class Output(BaseModel):
    """
    Output send to caller
    """

    message: str = Field(
        title="Job status information",
        description="Contains error information of other relevant ORCA ingest job information.",
        json_schema_extra={
            "example": ["No files copied because of exclusion configuration.", "This is a test"],
        },
    )
    error_code: str | None = Field(
        default=None,
        alias="errorCode",
        title="ORCA Error Code",
        description="Error code used by ORCA support to help determine issues.",
        json_schema_extra={
            "example": ["null", "BadConfig"],
        },
    )
