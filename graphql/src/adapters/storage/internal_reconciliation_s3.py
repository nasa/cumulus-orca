import dataclasses

import pydantic

# noinspection PyPackageRequirements
import strawberry

from src.entities.files import FileLocation

MANIFEST_FILES_KEY = "files"
FILES_KEY_KEY = "key"


@strawberry.input  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclasses.dataclass
class AWSS3FileLocation(pydantic.BaseModel, FileLocation):
    # IMPORTANT: Whenever properties are added/removed/modified/renamed, update constructor.
    bucket_name: str
    key: str

    # Overriding constructor to give us type/name hints for Pydantic class.
    def __init__(self, bucket_name: str, key: str):
        # This call to __init__ will NOT automatically update when performing renames.
        super().__init__(bucket_name=bucket_name, key=key)
