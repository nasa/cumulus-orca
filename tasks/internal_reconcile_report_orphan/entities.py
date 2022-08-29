import dataclasses


@dataclasses.dataclass
class OrphanRecord:
    key_path: str
    etag: str
    last_update: int
    size_in_bytes: int
    storage_class: str
