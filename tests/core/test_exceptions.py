import pytest

from sportscli.core.exceptions import (
    ApiError,
    AuthError,
    ConfigError,
    NetworkError,
    RateLimitError,
    SportsCLIError,
)


class TestHierarchy:
    def test_sports_cli_error_is_base_exception(self):
        assert issubclass(SportsCLIError, Exception)

    def test_network_error_is_sports_cli_error(self):
        assert issubclass(NetworkError, SportsCLIError)

    def test_config_error_is_sports_cli_error(self):
        assert issubclass(ConfigError, SportsCLIError)

    def test_api_error_is_sports_cli_error(self):
        assert issubclass(ApiError, SportsCLIError)

    def test_auth_error_is_api_error(self):
        assert issubclass(AuthError, ApiError)

    def test_rate_limit_error_is_api_error(self):
        assert issubclass(RateLimitError, ApiError)

    def test_auth_error_is_sports_cli_error(self):
        assert issubclass(AuthError, SportsCLIError)

    def test_rate_limit_error_is_sports_cli_error(self):
        assert issubclass(RateLimitError, SportsCLIError)


class TestApiError:
    def test_stores_status_code(self):
        err = ApiError("not found", 404)
        assert err.status_code == 404

    def test_message_is_accessible(self):
        err = ApiError("something went wrong", 500)
        assert str(err) == "something went wrong"

    def test_status_code_defaults_to_none(self):
        err = ApiError("no code given")
        assert err.status_code is None

    def test_is_catchable_as_sports_cli_error(self):
        with pytest.raises(SportsCLIError):
            raise ApiError("test", 400)


class TestAuthError:
    def test_stores_status_code_401(self):
        err = AuthError("unauthorized", 401)
        assert err.status_code == 401

    def test_stores_status_code_403(self):
        err = AuthError("forbidden", 403)
        assert err.status_code == 403

    def test_is_catchable_as_api_error(self):
        with pytest.raises(ApiError):
            raise AuthError("forbidden", 403)

    def test_is_catchable_as_sports_cli_error(self):
        with pytest.raises(SportsCLIError):
            raise AuthError("unauthorized", 401)


class TestRateLimitError:
    def test_stores_status_code(self):
        err = RateLimitError("too many requests", 429)
        assert err.status_code == 429

    def test_is_catchable_as_api_error(self):
        with pytest.raises(ApiError):
            raise RateLimitError("slow down", 429)


class TestNetworkError:
    def test_message(self):
        err = NetworkError("connection refused")
        assert str(err) == "connection refused"

    def test_is_catchable_as_sports_cli_error(self):
        with pytest.raises(SportsCLIError):
            raise NetworkError("timeout")


class TestConfigError:
    def test_message(self):
        err = ConfigError("file not found")
        assert str(err) == "file not found"

    def test_is_catchable_as_sports_cli_error(self):
        with pytest.raises(SportsCLIError):
            raise ConfigError("bad config")
