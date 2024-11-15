"""Env Settings."""

from pydantic_settings import BaseSettings


class EnvSettings(BaseSettings):
    """Class for environment."""

    # Certs
    SSL_KEYFILE: str
    SSL_CERTFILE: str


env = EnvSettings()
