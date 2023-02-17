"""
Test the logging helper class
"""
import logging

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.helpers.config import Config
from fotoobo.helpers.log import Log


class TestLog:
    """
    Class to test the Log class
    """

    @pytest.mark.parametrize(
        "config,log_switch,log_level",
        (pytest.param(Config(), None, None, id="default logging config"),),
    )
    def test_configure_logging(
        self, config: Config, log_switch: bool, log_level: str, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Test the configure_logging() method
        Args:
            log_switch:
            log_level:

        Returns:

        """

        monkeypatch.setattr("fotoobo.helpers.log.config", config)

        Log.configure_logging(log_switch, log_level)

        fotoobo_logger = logging.getLogger("fotoobo")
        requests_logger = logging.getLogger("requests")
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_connectionpool_logger = logging.getLogger("urllib3.connectionpool")

        assert fotoobo_logger.disabled is True
        assert requests_logger.level == logging.CRITICAL
        assert urllib3_logger.level == logging.CRITICAL
        assert urllib3_connectionpool_logger.level == logging.CRITICAL
