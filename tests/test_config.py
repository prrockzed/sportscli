import json
import pytest
from pathlib import Path

from sportscli.config import get_api_key, load, save, set_api_key
from sportscli.core.exceptions import ConfigError


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Redirect all config operations to a temp directory for every test."""
    monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))


class TestLoad:
    def test_returns_empty_dict_when_file_missing(self):
        assert load() == {}

    def test_returns_parsed_config(self, tmp_path):
        data = {"version": "1", "api_keys": {"cricket": "abc123"}}
        (tmp_path / "config.json").write_text(json.dumps(data))
        assert load() == data

    def test_raises_config_error_on_malformed_json(self, tmp_path):
        (tmp_path / "config.json").write_text("not valid json {{{{")
        with pytest.raises(ConfigError):
            load()

    def test_raises_config_error_on_unreadable_file(self, tmp_path):
        path = tmp_path / "config.json"
        path.write_text("{}")
        path.chmod(0o000)
        try:
            with pytest.raises(ConfigError):
                load()
        finally:
            path.chmod(0o644)  # restore so tmp_path cleanup works


class TestSave:
    def test_writes_valid_json(self, tmp_path):
        data = {"version": "1", "api_keys": {"football": "xyz"}}
        save(data)
        written = json.loads((tmp_path / "config.json").read_text())
        assert written == data

    def test_overwrites_existing_file(self):
        save({"api_keys": {"cricket": "old"}})
        save({"api_keys": {"cricket": "new"}})
        assert load()["api_keys"]["cricket"] == "new"

    def test_creates_config_dir_if_missing(self, tmp_path, monkeypatch):
        nested = tmp_path / "deep" / "nested"
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(nested))
        save({"version": "1"})
        assert (nested / "config.json").exists()


class TestGetApiKey:
    def test_returns_none_when_key_not_set(self):
        assert get_api_key("cricket") is None

    def test_returns_none_for_unknown_sport(self):
        set_api_key("cricket", "key")
        assert get_api_key("tennis") is None

    def test_returns_none_when_config_file_missing(self):
        assert get_api_key("football") is None


class TestSetApiKey:
    def test_stored_key_is_retrievable(self):
        set_api_key("cricket", "mykey123")
        assert get_api_key("cricket") == "mykey123"

    def test_multiple_keys_coexist(self):
        set_api_key("cricket", "cricket-key")
        set_api_key("football", "football-key")
        assert get_api_key("cricket") == "cricket-key"
        assert get_api_key("football") == "football-key"

    def test_overwrites_existing_key(self):
        set_api_key("cricket", "old-key")
        set_api_key("cricket", "new-key")
        assert get_api_key("cricket") == "new-key"

    def test_initialises_version_field(self):
        set_api_key("cricket", "key")
        assert load()["version"] == "1"

    def test_does_not_overwrite_other_keys(self):
        set_api_key("cricket", "c-key")
        set_api_key("football", "f-key")
        # update cricket, football should still be there
        set_api_key("cricket", "c-key-v2")
        assert get_api_key("football") == "f-key"
