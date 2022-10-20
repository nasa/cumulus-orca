import logging
import re

from orca_shared.database.entities import PostgresConnectionInfo


# todo: add unit tests
def validate_config(config: PostgresConnectionInfo, logger: logging.Logger) -> None:
    validate_postgres_name(config.user_username, "User username", logger)
    validate_postgres_name(config.admin_username, "Admin username", logger)

    _validate_password(config.user_password, "User", logger)
    # todo: More validations? These were just pulled from db_deploy

    validate_postgres_name(config.user_database_name, "User database name", logger)
    validate_postgres_name(config.admin_database_name, "Admin database name", logger)


def _validate_password(password: str, context: str, logger: logging.Logger) -> None:
    """
    Validates the given password against Orca restrictions.

    Raises:
        Exception: If value is empty or less than 12 characters.
    """
    if password is None or len(password) < 12:
        msg = f"{context} password must be at least 12 characters long."
        logger.critical(msg)
        raise Exception(msg)


def validate_postgres_name(name: str, context: str, logger: logging.Logger) -> None:
    """
    Validates the given name against documented Postgres restrictions.
    https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS

    Raises:
        Exception: If value is empty, is more than 63 characters, or contains illegal characters.
    """
    if name is None or len(name) == 0:
        msg = f"{context} must be non-empty."
        logger.critical(msg)
        raise Exception(msg)
    if len(name) > 63:
        msg = f"{context} must be less than 64 characters."
        logger.critical(msg)
        raise Exception(msg)
    # noinspection RegExpSimplifiable
    # todo: Add support for non-english characters mentioned in postgres docs. ORCA-572
    if not re.compile("^[a-zA-Z_][a-zA-Z0-9_$]*$").match(name):
        msg = f"{context} must start with an English letter or '_' " \
              "and contain only English letters, numbers, '$', or '_'."
        logger.critical(msg)
        raise Exception(msg)
