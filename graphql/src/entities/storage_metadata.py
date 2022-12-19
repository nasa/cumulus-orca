import dataclasses

import pydantic

# noinspection PyPackageRequirements
import strawberry


@strawberry.type  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclasses.dataclass
class StorageSchemaVersion(pydantic.BaseModel):
    # IMPORTANT: Whenever properties are added/removed/modified/renamed, update constructor.
    version: int

    # Overriding constructor to give us type/name hints for Pydantic class.
    def __init__(self, version: int):
        # This call to __init__ will NOT automatically update when performing renames.
        super().__init__(version=version)
