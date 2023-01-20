import dataclasses
from typing import Optional

import pydantic

# noinspection PyPackageRequirements
import strawberry


@strawberry.type  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclasses.dataclass
class Phantom(pydantic.BaseModel):
    # IMPORTANT: Whenever properties are added/removed/modified/renamed, update constructor.
    job_id: int
    collection_id: str
    granule_id: str
    filename: str
    key_path: str
    orca_etag: str
    orca_last_update: int
    orca_size_in_bytes: int
    orca_storage_class: str

    @dataclasses.dataclass
    class Cursor:
        job_id: int = None
        collection_id: str = None
        granule_id: str = None
        key_path: str = None

    # Overriding constructor to give us type/name hints for Pydantic class.
    def __init__(self,
                 job_id: int,
                 collection_id: str,
                 granule_id: str,
                 filename: str,
                 key_path: str,
                 orca_etag: str,
                 orca_last_update: int,
                 orca_size_in_bytes: int,
                 orca_storage_class: str,
                 ):
        # This call to __init__ will NOT automatically update when performing renames.
        super().__init__(
            job_id=job_id,
            collection_id=collection_id,
            granule_id=granule_id,
            filename=filename,
            key_path=key_path,
            orca_etag=orca_etag,
            orca_last_update=orca_last_update,
            orca_size_in_bytes=orca_size_in_bytes,
            orca_storage_class=orca_storage_class,
        )

    def get_cursor(self):
        return Mismatch.Cursor(
            job_id=self.job_id,
            collection_id=self.collection_id,
            granule_id=self.granule_id,
            key_path=self.key_path,
        )


@strawberry.type  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclasses.dataclass
class Mismatch(pydantic.BaseModel):
    # IMPORTANT: Whenever properties are added/removed/modified/renamed, update constructor.
    job_id: int
    collection_id: str
    granule_id: str
    filename: str
    key_path: str
    cumulus_archive_location: str
    orca_etag: str
    s3_etag: str
    orca_last_update: int
    s3_last_update: int
    orca_size_in_bytes: int
    s3_size_in_bytes: int
    orca_storage_class: str
    s3_storage_class: str
    discrepancy_type: str
    comment: Optional[str]

    @dataclasses.dataclass
    class Cursor:
        job_id: int = None
        collection_id: str = None
        granule_id: str = None
        key_path: str = None

    # Overriding constructor to give us type/name hints for Pydantic class.
    def __init__(self,
                 job_id: int,
                 collection_id: str,
                 granule_id: str,
                 filename: str,
                 key_path: str,
                 cumulus_archive_location: str,
                 orca_etag: str,
                 s3_etag: str,
                 orca_last_update: int,
                 s3_last_update: int,
                 orca_size_in_bytes: int,
                 s3_size_in_bytes: int,
                 orca_storage_class: str,
                 s3_storage_class: str,
                 discrepancy_type: str,
                 comment: Optional[str],
                 ):
        # This call to __init__ will NOT automatically update when performing renames.
        super().__init__(
            job_id=job_id,
            collection_id=collection_id,
            granule_id=granule_id,
            filename=filename,
            key_path=key_path,
            cumulus_archive_location=cumulus_archive_location,
            orca_etag=orca_etag,
            s3_etag=s3_etag,
            orca_last_update=orca_last_update,
            s3_last_update=s3_last_update,
            orca_size_in_bytes=orca_size_in_bytes,
            s3_size_in_bytes=s3_size_in_bytes,
            orca_storage_class=orca_storage_class,
            s3_storage_class=s3_storage_class,
            discrepancy_type=discrepancy_type,
            comment=comment,
        )

    def get_cursor(self):
        return Mismatch.Cursor(
            job_id=self.job_id,
            collection_id=self.collection_id,
            granule_id=self.granule_id,
            key_path=self.key_path,
        )
