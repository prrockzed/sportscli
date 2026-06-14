import json
import os
import tempfile
from pathlib import Path

from sportscli.core.exceptions import ConfigError

_CONFIG_DIR_ENV = "SPORTSCLI_CONFIG_DIR"
_CONFIG_FILE = "config.json"


def get_config_path() -> Path:
    if env := os.environ.get(_CONFIG_DIR_ENV):
        config_dir = Path(env)
    else:
        try:
            from platformdirs import user_config_dir

            config_dir = Path(user_config_dir("sportscli"))
        except ImportError:
            config_dir = Path.home() / ".config" / "sportscli"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / _CONFIG_FILE


def load() -> dict:
    path = get_config_path()
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        raise ConfigError(f"Failed to read config at {path}: {exc}") from exc


def save(config: dict) -> None:
    path = get_config_path()
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            delete=False,
            suffix=".tmp",
        ) as tmp:
            json.dump(config, tmp, indent=2)
            tmp_path = Path(tmp.name)
        tmp_path.replace(path)
    except OSError as exc:
        raise ConfigError(f"Failed to save config: {exc}") from exc


def get_api_key(sport: str) -> str | None:
    config = load()
    return config.get("api_keys", {}).get(sport)


def set_api_key(sport: str, key: str) -> None:
    config = load()
    config.setdefault("version", "1")
    config.setdefault("api_keys", {})[sport] = key
    save(config)


def get_favourites() -> dict:
    return load().get("favourites", {})


def add_favourite(category: str, value: str) -> None:
    config = load()
    config.setdefault("version", "1")
    favs = config.setdefault("favourites", {})
    items: list = favs.setdefault(category, [])
    if value not in items:
        items.append(value)
    save(config)


def remove_favourite(category: str, value: str) -> bool:
    """Remove a favourite. Returns True if it was present, False otherwise."""
    config = load()
    favs = config.get("favourites", {})
    items: list = favs.get(category, [])
    if value not in items:
        return False
    items.remove(value)
    config["favourites"][category] = items
    save(config)
    return True
