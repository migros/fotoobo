"""
Test the config helper
"""

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch

from fotoobo.helpers.config import Config


class TestConfig:
    """Test the config dataclass"""

    @staticmethod
    def test_config() -> None:
        """test it"""
        config = Config()
        assert config.backup_dir == ""
        assert config.inventory_file == "inventory.yaml"
        assert not config.logging
        assert not config.audit_logging
        assert config.log_file == ""
        assert config.log_level == "INFO"
        assert not config.no_logo

    @staticmethod
    def test_load_configuration(monkeypatch: MonkeyPatch) -> None:
        """test load configuration from file"""
        monkeypatch.setattr("fotoobo.helpers.files.os.path.isfile", MagicMock(return_value=True))
        monkeypatch.setattr(
            "fotoobo.helpers.config.load_yaml_file", MagicMock(return_value={"backup_dir": "test"})
        )
        config = Config()
        assert config.backup_dir == ""
        config.load_configuration("dummy")
        assert config.backup_dir == "test"
