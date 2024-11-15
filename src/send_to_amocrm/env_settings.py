"""Env Settings."""

from pydantic_settings import BaseSettings


class EnvSettings(BaseSettings):
    """Class for environment."""

    # amoCRM API chats
    AMOCRM_CHANNEL_SECRET: str
    AMOCRM_CHANNEL_ID: str
    AMOCRM_SCOPE_ID: str
    AMOCRM_BOT_ID: str
    AMOCRM_BOT_CLIENT_ID: str
    AMOCRM_BOT_NAME: str


env = EnvSettings()
