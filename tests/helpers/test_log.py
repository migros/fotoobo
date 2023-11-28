"""
Test the logging helper class
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from logging.handlers import RotatingFileHandler, SysLogHandler
from syslog import LOG_USER
from typing import List, Type
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from rich.logging import RichHandler

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.config import Config
from fotoobo.helpers.log import Log, SysLogFormatter


@dataclass
class LoggerConfig:
    """
    A class for holding the expected LoggerConfig for the configure_logging() tests
    """

    disabled: bool
    log_level: int
    handlers: List[Type[logging.Handler]]


@pytest.fixture(name="syslog_formatter")
def fixture_syslog_formatter() -> SysLogFormatter:
    """
    Returns an initialized SysLogFormatter for testing
    Returns:
        SysLogFormatter: An initialized SysLogFormatter instance
    """

    syslog_formatter = SysLogFormatter(facility=LOG_USER)
    syslog_formatter.user = "dummy_user"
    syslog_formatter.hostname = "dummy.host"

    return syslog_formatter


class TestSysLogFormatter:
    """
    Class to test the SysLogFormatter class
    """

    @pytest.mark.parametrize(
        "log_record,expected_string",
        [
            pytest.param(
                logging.LogRecord(
                    name="fotoobo",
                    pathname="dummy.py",
                    lineno=3,
                    level=logging.DEBUG,
                    msg="test_message",
                    exc_info=None,
                    args=None,
                ),
                "<15>1 1970-01-01T%s:00:00%s dummy.host fotoobo 3456 - - "
                "username=dummy_user test_message",
                id="debug log",
            ),
            pytest.param(
                logging.LogRecord(
                    name="fotoobo",
                    pathname="dummy.py",
                    lineno=3,
                    level=logging.INFO,
                    msg="test_message",
                    exc_info=None,
                    args=None,
                ),
                "<14>1 1970-01-01T%s:00:00%s dummy.host fotoobo 3456 - - "
                "username=dummy_user test_message",
                id="info log",
            ),
            pytest.param(
                logging.LogRecord(
                    name="fotoobo",
                    pathname="dummy.py",
                    lineno=3,
                    level=logging.WARNING,
                    msg="test_message",
                    exc_info=None,
                    args=None,
                ),
                "<12>1 1970-01-01T%s:00:00%s dummy.host fotoobo 3456 - - "
                "username=dummy_user test_message",
                id="warning log",
            ),
            pytest.param(
                logging.LogRecord(
                    name="fotoobo",
                    pathname="dummy.py",
                    lineno=3,
                    level=logging.ERROR,
                    msg="test_message",
                    exc_info=None,
                    args=None,
                ),
                "<11>1 1970-01-01T%s:00:00%s dummy.host fotoobo 3456 - - "
                "username=dummy_user test_message",
                id="error log",
            ),
            pytest.param(
                logging.LogRecord(
                    name="fotoobo",
                    pathname="dummy.py",
                    lineno=3,
                    level=logging.CRITICAL,
                    msg="test_message",
                    exc_info=None,
                    args=None,
                ),
                "<10>1 1970-01-01T%s:00:00%s dummy.host fotoobo 3456 - - "
                "username=dummy_user test_message",
                id="critical log",
            ),
        ],
    )
    def test_format(
        self,
        syslog_formatter: SysLogFormatter,
        log_record: logging.LogRecord,
        expected_string: str,
    ) -> None:
        """
        Test the format() method
        Args:
            syslog_formatter:
            log_record:
            expected_string:

        Returns:

        """
        # Patch some log_record parts
        log_record.created = 0
        log_record.process = 3456

        # Make the tzinfo part of the expected message dynamic, so tests run all over the world
        tzinfo = datetime.fromtimestamp(0).astimezone().strftime("%z")
        hour = datetime.fromtimestamp(0).strftime("%H")
        expected_string = expected_string % (hour, f"{tzinfo[0:3]}:{tzinfo[3:]}")

        assert syslog_formatter.format(log_record) == expected_string

    def test_format_with_unknown_loglevel(self, syslog_formatter: SysLogFormatter) -> None:
        """
        Test the format() method, when an unknown level is given.
        It should raise a NotImplementedError in this case

        Args:
            syslog_formatter:

        Returns:

        """
        log_record = logging.LogRecord(
            name="fotoobo",
            pathname="dummy.py",
            lineno=3,
            level=logging.CRITICAL,
            msg="test_message",
            exc_info=None,
            args=None,
        )

        log_record.levelname = "UNKNOWN"

        with pytest.raises(NotImplementedError):
            syslog_formatter.format(log_record)


class TestLog:
    """
    Class to test the Log class
    """

    @pytest.mark.parametrize(
        "config,quiet,log_level,expected_fotoobo_logger_config,expected_audit_logger_config",
        (
            pytest.param(
                Config(),
                True,
                None,
                LoggerConfig(disabled=True, log_level=logging.WARNING, handlers=[]),
                LoggerConfig(disabled=True, log_level=logging.INFO, handlers=[]),
                id="default logging config 1",
            ),
            pytest.param(
                Config(),
                None,
                None,
                LoggerConfig(disabled=False, log_level=logging.WARNING, handlers=[RichHandler]),
                LoggerConfig(disabled=True, log_level=logging.INFO, handlers=[]),
                id="default logging config 2",
            ),
            pytest.param(
                Config(logging={"enabled": True, "level": "INFO", "log_console": {}}),
                None,
                None,
                LoggerConfig(
                    disabled=False,
                    log_level=logging.INFO,
                    handlers=[RichHandler],
                ),
                LoggerConfig(disabled=True, log_level=logging.INFO, handlers=[]),
                id="simple log configuration from config file",
            ),
            pytest.param(
                Config(
                    logging={
                        "level": "DEBUG",
                        "log_console": {},
                        "log_file": {
                            "name": "test.log",
                        },
                        "log_syslog": {"host": "1.2.3.4", "port": 123, "protocol": "UDP"},
                    }
                ),
                None,
                None,
                LoggerConfig(
                    disabled=False,
                    log_level=logging.DEBUG,
                    handlers=[RichHandler, RotatingFileHandler, SysLogHandler],
                ),
                LoggerConfig(disabled=True, log_level=logging.INFO, handlers=[]),
                id="full log configuration from config file",
            ),
        ),
    )
    # pylint: disable=too-many-arguments
    def test_configure_logging(
        self,
        config: Config,
        quiet: bool,
        log_level: str,
        expected_fotoobo_logger_config: LoggerConfig,
        expected_audit_logger_config: LoggerConfig,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Test the configure_logging() method
        Args:
            quiet:
            log_level:

        Returns:

        """
        monkeypatch.setattr("fotoobo.helpers.log.config", config)

        # The 3rd party loggers should get the same config in any case
        requests_logger = logging.getLogger("requests")
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_connectionpool_logger = logging.getLogger("urllib3.connectionpool")

        # Get & check the loggers used by fotoobo
        fotoobo_logger = logging.getLogger("fotoobo")
        audit_logger = logging.getLogger("audit")

        # Overwrite the disabled flag (disabled by default for testing)
        monkeypatch.setattr(fotoobo_logger, "disabled", False)
        monkeypatch.setattr(audit_logger, "disabled", False)

        # Empty handlers to remove potentially existing logging config
        monkeypatch.setattr(fotoobo_logger, "handlers", [])
        monkeypatch.setattr(audit_logger, "handlers", [])

        Log.configure_logging(quiet, log_level)

        if expected_fotoobo_logger_config.disabled:
            assert fotoobo_logger.disabled is True
            assert requests_logger.level == logging.CRITICAL
            assert urllib3_logger.level == logging.CRITICAL

        else:
            assert fotoobo_logger.level == expected_fotoobo_logger_config.log_level
            # All handlers should be set
            assert len(fotoobo_logger.handlers) == len(expected_fotoobo_logger_config.handlers)
            # Check that the right handlers are set
            for handler in fotoobo_logger.handlers:
                assert type(handler) in expected_fotoobo_logger_config.handlers

            if config.logging:
                assert requests_logger.level == expected_fotoobo_logger_config.log_level
                assert urllib3_logger.level == expected_fotoobo_logger_config.log_level
            else:
                assert requests_logger.level == logging.CRITICAL
                assert urllib3_logger.level == logging.CRITICAL

        if expected_audit_logger_config.disabled:
            assert audit_logger.disabled is True
        else:
            assert audit_logger.level == expected_audit_logger_config.log_level
            for handler in audit_logger.handlers:
                assert type(handler) in expected_audit_logger_config.handlers

        assert urllib3_connectionpool_logger.level == logging.CRITICAL

        if quiet:
            assert fotoobo_logger.disabled is True

    def test_audit(self, monkeypatch: MonkeyPatch) -> None:
        """
        Test the Log.audit() static method.

        It should call the info method of the audit logger.

        Returns:
        """
        logger = logging.getLogger("fotoobo")
        audit_logger = logging.getLogger("audit")
        audit_patch = MagicMock()
        monkeypatch.setattr(audit_logger, "info", audit_patch)

        logger.audit("test")  # type: ignore

        audit_patch.assert_called_with("test")

    @pytest.mark.parametrize(
        "config",
        (
            pytest.param(
                Config(
                    logging={
                        "enabled": True,
                        "level": "DEBUG",
                        "log_console": {},
                        "log_file": {
                            "name": "test.log",
                        },
                        "log_syslog": {
                            "host": "notexisting.syslog.host.local",
                            "port": 123,
                            "protocol": "UDP",
                        },
                    }
                ),
                id="Normal logging",
            ),
            pytest.param(
                Config(
                    logging={
                        "enabled": False,
                    },
                    audit_logging={
                        "enabled": True,
                        "level": "DEBUG",
                        "log_console": {},
                        "log_file": {
                            "name": "test.log",
                        },
                        "log_syslog": {
                            "host": "notexisting.syslog.host.local",
                            "port": 123,
                            "protocol": "UDP",
                        },
                    },
                ),
                id="Audit logging",
            ),
        ),
    )
    def test_logging_with_syslog_server_not_available(
        self, config: Config, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Test that fotoobo closes itself sanely when the configured syslog server is not available.

        Args:
            monkeypatch:

        Returns:

        """

        monkeypatch.setattr("fotoobo.helpers.log.config", config)

        monkeypatch.setattr(
            "fotoobo.helpers.log.SysLogHandler",
            MagicMock(side_effect=OSError("[Errno 113] No route to host")),
        )

        with pytest.raises(GeneralError, match="Cannot configure SysLog logging: *"):
            Log.configure_logging(True, "INFO")
