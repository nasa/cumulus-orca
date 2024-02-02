from logging import Logger

from . import entities, schema


def get_settings(
    logger: Logger,
    override: schema.OverrideSettings | None = None,
) -> entities.Settings:
    """
    Retrieves final settings for job by looking at the default
    and override values for the various items. Override values
    take precedence.
    """

    # Get the environment variables and default settings
    _env_settings = schema.DefaultSettings().model_dump()

    if override is not None:
        # Setup environmental overrides
        _override_env_dict = override.model_dump()

        # Remove key/value pairs that have a value of None
        _override_env_dict = {
            key: value for key, value in _override_env_dict.items() if value is not None
        }

        # There is a pydantic-settings bug so we can't pass
        # the overrides directly to EnvSettings as a dictionary
        # like "**_override_env_dict" so we need to do our
        # override of values via dict keys and values.
        for key, value in _override_env_dict.items():
            logger.debug(f"Overriding setting {key} with {value}")
            _env_settings[key] = value

    return entities.Settings(**_env_settings)
