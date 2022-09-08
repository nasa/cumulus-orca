import sqlalchemy.engine.create
from sqlalchemy.engine import make_url
from sqlalchemy.future import Engine


def create_engine(uri: str) -> Engine:
    """
    Creates a sqlalchemy engine based on the given uri.

    Args:
        uri: The URI to use for connecting to the database.

    Returns:
        Engine object for creating database connections.
    """
    connection_url = make_url(uri)
    return sqlalchemy.engine.create.create_engine(connection_url, future=True)
