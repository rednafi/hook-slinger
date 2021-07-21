from __future__ import annotations

import typing
from pathlib import Path

import httpx
import toml

if typing.TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Any, NoReturn


class ConfigFormatError(Exception):
    pass


class ConfigNotFoundError(Exception):
    pass


class ConfigKeyMissingError(Exception):
    pass


def validate_config(
    config: MutableMapping[str, Any]
) -> MutableMapping[str, Any] | NoReturn:

    for key in ("groups",):
        if not key in config:
            raise ConfigKeyMissingError(
                f"Key '{key}' must be present in the 'config.toml' file"
            )
    return config


def read_config() -> MutableMapping[str, Any] | NoReturn:
    toml_path = Path(__file__).parent.parent / "config.toml"

    if not toml_path.exists():
        raise ConfigNotFoundError(
            "Did to forget to add 'config.toml' to your root directory?"
        )

    try:
        config = toml.load(str(toml_path))

    except toml.TomlDecodeError as exc:
        raise ConfigFormatError("Error in your config file format. \n") from exc

    # Validate and config
    return validate_config(config)


print(read_config())

# def save_payload_to_db():
#     ...


# def send_post_request(url: str, ) -> None:
#     with httpx.Client(http2=True) as session:
