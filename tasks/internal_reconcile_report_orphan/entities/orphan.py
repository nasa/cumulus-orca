import dataclasses
from typing import List


@dataclasses.dataclass
class OrphanRecord:
    key_path: str
    etag: str
    last_update: int
    size_in_bytes: int
    storage_class: str


@dataclasses.dataclass
class OrphanRecordFilter:
    job_id: str
    page_index: int
    page_size: int


@dataclasses.dataclass
class OrphanRecordPage:
    orphans: List[OrphanRecord]
    another_page: bool
