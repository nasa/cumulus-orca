from typing import List, Literal

from pydantic import BaseModel, Field

StorageTypes = Literal["GLACIER", "DEEP_ARCHIVE"]


class Settings(BaseModel):
    """
    Provides all the user settings
    needed for performing the task.
    """

    storage_class: StorageTypes = Field(
        title="ORCA storage class",
        description="The storage class used for storing the files.",
    )
    orca_bucket: str = Field(
        title="Default ORCA archiving bucket",
        description="Default ORCA storage bucket to use for backed up data.",
    )
    multipart_chunksize: int = Field(
        title="Multipart Chunk Size in Megabytes",
        description="The default multipart chunk size affects performance and copy time.",
    )
    excluded_files_regex: List[str] | None = Field(
        title="List of regular expressions",
        description="Regular expressions that will exclude files from being backed up in ORCA.",
    )
