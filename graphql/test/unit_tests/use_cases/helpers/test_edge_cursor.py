import unittest

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
