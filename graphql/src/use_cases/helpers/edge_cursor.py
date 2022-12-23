import json
from base64 import b64decode, b64encode
from typing import Generic

from src.entities.common import GenericType


class EdgeCursor:
    """
    Manages cursor information for a record set of information. This allows end users to go
    directly to a specific record or reproduce a page of data within reason. The two methods
    below handle common use cases for encoding and decoding cursor values to be used with paging
    and other record set information.
    """
    @staticmethod
    def encode_cursor(**kwargs: dict) -> str:
        """
        Creates a cursor value for a specific record.

        Args:
            kwargs: key/value dictionary with the column names and values needed for the cursor

        Returns:
            Base 64 encoded json string
        """
        # Change the dictionary to a JSON string
        values = json.dumps(kwargs)

        # Base 64 encode the string
        encoded_cursor = b64encode(values.encode('utf8'))

        return encoded_cursor.decode('utf8')

    @staticmethod
    def decode_cursor(cursor: str, filter_type: Generic[GenericType]) -> GenericType:
        """
        Decodes the cursor into a dictionary with column names as keys and
        corresponding values.

        Args:
            cursor: Base 64 encoded json string
            filter_type: Filter entity used to query to a specific record or pagination set

        Returns:
            Filter entity specified
        """
        # Decode string
        decoded_cursor = b64decode(cursor.encode('utf8'))

        # create dictionary from JSON
        kwargs = json.loads(decoded_cursor.decode('utf8'))

        # Create the Entity
        return filter_type(**kwargs)
