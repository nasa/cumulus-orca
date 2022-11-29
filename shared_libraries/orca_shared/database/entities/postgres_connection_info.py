import dataclasses


@dataclasses.dataclass
class PostgresConnectionInfo:
    admin_database_name: str
    admin_username: str
    admin_password: str
    user_username: str
    user_password: str
    user_database_name: str
    host: str
    port: str
