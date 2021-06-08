from typing import Dict, Any

from cumulus_logger import CumulusLogger

LOGGER = CumulusLogger()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the copy_to_glacier_cumulus_translator Lambda.
    Args:
        event: A dict with the following keys:
            TODO
        context: An object provided by AWS Lambda. Used for context tracking.

    Returns: A Dict with the following keys:
        TODO
    """
    LOGGER.setMetadata(event, context)

