import dataclasses
import unittest

from src.entities.internal_reconcile_report import Mismatch
from src.use_cases.helpers.edge_cursor import EdgeCursor


class TestEdgeCursor(unittest.TestCase):

    def test_encode_cursor_happy_path(self):
        """
        Generating a cursor from the same information should always return the same string.
        """
        result = EdgeCursor.encode_cursor(**{
            "apples": "red",
            "bananas": "yellow",
            "monitors": 1.5,
        })
        self.assertEqual(
            "eyJhcHBsZXMiOiAicmVkIiwgImJhbmFuYXMiOiAieWVsbG93IiwgIm1vbml0b3JzIjogMS41fQ==", result)

    def test_decode_cursor_happy_path(self):
        """
        Decoded cursors should be consistent.
        """
        result = EdgeCursor.decode_cursor(
            "eyJhcHBsZXMiOiAicmVkIiwgImJhbmFuYXMiOiAieWVsbG93IiwgIm1vbml0b3JzIjogMS41fQ==",
            dict
        )
        self.assertEqual({
            "apples": "red",
            "bananas": "yellow",
            "monitors": 1.5,
        },
            result)

    def test_encode_cursor_dataclass(self):
        dataclass = Mismatch.Cursor(
            job_id=1024,
            collection_id="some collection id",
            granule_id="some granule id",
            key_path="some key path",
        )
        result = EdgeCursor.encode_cursor(**dataclasses.asdict(dataclass))
        self.assertEqual(
            "eyJqb2JfaWQiOiAxMDI0LCAiY29sbGVjdGlvbl9pZCI6ICJzb21lIGNvbGxlY3Rpb24gaWQiLCAiZ3JhbnVsZ"
            "V9pZCI6ICJzb21lIGdyYW51bGUgaWQiLCAia2V5X3BhdGgiOiAic29tZSBrZXkgcGF0aCJ9",
            result)
        result = EdgeCursor.decode_cursor(
            "eyJqb2JfaWQiOiAxMDI0LCAiY29sbGVjdGlvbl9pZCI6ICJzb21lIGNvbGxlY3Rpb24gaWQiLCAiZ3JhbnVsZ"
            "V9pZCI6ICJzb21lIGdyYW51bGUgaWQiLCAia2V5X3BhdGgiOiAic29tZSBrZXkgcGF0aCJ9",
            Mismatch.Cursor
        )
        self.assertEqual(dataclass, result)
