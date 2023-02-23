"""
The logging helper class is used if you want to write logs to the screen or a file. It is set up
to do pretty printing screen output with rich and writing "normal" text to a logfile.
Basic logging options can be configured in the main configuration file. See config_helper.py
"""
import logging
import logging.config
import os
import pwd
import socket
from datetime import datetime
from logging.handlers import RotatingFileHandler, SysLogHandler
from typing import Optional, Union
from syslog import LOG_AUTH, LOG_CRIT, LOG_DEBUG, LOG_ERR, LOG_INFO, LOG_USER, LOG_WARNING

from rich.logging import RichHandler

from fotoobo.exceptions import GeneralError, GeneralWarning
from fotoobo.helpers.config import config
from fotoobo.helpers.files import load_yaml_file

logger = logging.getLogger("fotoobo")
audit_logger = logging.getLogger("audit")


class SysLogFormatter(logging.Formatter):
    """
    Handles syslog formats
    """

    def __init__(self, facility: int, fmt: str = "%(message)s", datefmt: Optional[str] = None):
        """
        Initialize the logger

        Args:
            facility:
        """
        self.facility = facility

        # Need to do this like this, to have the GitLab pipeline work
        # See https://stackoverflow.com/questions/4399617/python-os-getlogin-problem
        self.user = pwd.getpwuid(os.getuid())[0]
        self.hostname = socket.gethostname()

        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the message

        Args:
            record:

        Returns:

        """

        if record.levelname == "DEBUG":
            level: int = LOG_DEBUG
        elif record.levelname == "INFO":
            level = LOG_INFO
        elif record.levelname == "WARNING":
            level = LOG_WARNING
        elif record.levelname == "ERROR":
            level = LOG_ERR
        elif record.levelname == "CRITICAL":
            level = LOG_CRIT
        else:
            raise NotImplementedError(f"Loglevel {record.levelname} cannot be processed!")

        msg_id = "AUDIT" if self.facility == LOG_AUTH else "-"

        prival = self.facility + level
        timestamp = datetime.fromtimestamp(record.created).astimezone().isoformat()

        return (
            " ".join(
                [
                    # Syslog header parts
                    f"<{prival}>1",
                    timestamp,
                    "fotoobo",
                    f"{self.hostname}",
                    f"{record.process}",
                    msg_id,
                    "-",
                    # Syslog message parts
                    f"username={self.user}",
                ]
            )
            + " "
            + super().format(record)
        )


class Log:
    """
    The logger class for log control.
    """

    @staticmethod
    def configure_logging(log_switch: Union[bool, None], log_level: Union[str, None]) -> None:
        """
        This function will configure the logging for fotoobo

        Args:
            log_switch: Whether we globally turn logging off or on
            log_level:  The desired log_level (given by CLI argument)

        Returns:
            Nothing

        Raises:
            GeneralError    On unrecoverable errors (usually on non-existing/empty or
                            invalid logging configuration file
        """
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        # Make some defaults for (some chatty) external libraries
        logging.getLogger("requests").setLevel(logging.CRITICAL)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)

        # If we have a logging configuration file, use this to configure logging
        if config.logging and config.logging.get("log_configuration_file"):
            if logging_config := load_yaml_file(config.logging["log_configuration_file"]):
                try:
                    logging.config.dictConfig(dict(logging_config))

                except ValueError as error:
                    raise GeneralError(f"Cannot configure logging: {str(error)}") from error
                except TypeError as error:
                    raise GeneralError(f"Cannot configure logging: {str(error)}") from error
                except AttributeError as error:
                    raise GeneralError(f"Cannot configure logging: {str(error)}") from error
                except ImportError as error:
                    raise GeneralError(f"Cannot configure logging: {str(error)}") from error

            # If the configuration file cannot be found or is empty
            else:
                raise GeneralError(
                    "Cannot configure logging: Configuration file "
                    f'"{config.logging["log_configuration_file"]}" not found or empty!'
                )

        # If there is no logging configuration file, use the basic logging configuration
        else:
            # The log level given as command line option has precedence over anything other
            if log_level and log_level not in [
                "CRITICAL",
                "ERROR",
                "WARNING",
                "INFO",
                "DEBUG",
            ]:
                raise GeneralWarning(f"Loglevel {log_level} not known")

            if log_switch and not config.logging:
                logging.basicConfig(
                    level=log_level or logging.INFO,
                    format="[grey37]%(name)s[/] %(message)s",
                    datefmt="[%X]",
                    handlers=[RichHandler(markup=True)],
                )

            else:
                if config.logging and (config.logging["enabled"] or log_switch):
                    log_level = log_level if log_level else config.logging["level"]

                    logger.setLevel(log_level)
                    logging.getLogger("requests").setLevel(log_level)
                    logging.getLogger("urllib3").setLevel(log_level)

                    logger.handlers = []

                    # Configure console logging
                    if "log_console" in config.logging:
                        console_handler = RichHandler(markup=True)

                        console_handler.setFormatter(
                            logging.Formatter(fmt="[grey37]%(name)s[/] %(message)s", datefmt="[%X]")
                        )

                        logger.addHandler(console_handler)

                    if "log_file" in config.logging:
                        file_handler = RotatingFileHandler(
                            filename=config.logging["log_file"]["name"],
                            maxBytes=10485760,  # 10 MByte
                            backupCount=3,
                        )

                        file_handler.setFormatter(
                            logging.Formatter(
                                "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d: "
                                "%(message)s"
                            )
                        )

                        logger.addHandler(file_handler)

                    if "log_syslog" in config.logging:
                        syslog_handler = SysLogHandler(
                            address=(
                                config.logging["log_syslog"]["host"],
                                int(config.logging["log_syslog"]["port"]),
                            ),
                            socktype=socket.SOCK_STREAM
                            if config.logging["log_syslog"]["protocol"] == "TCP"
                            else socket.SOCK_DGRAM,
                        )

                        syslog_handler.setFormatter(SysLogFormatter(LOG_USER))

                        logger.addHandler(syslog_handler)

                else:
                    logger.disabled = True

                # Configure audit logging
                if config.audit_logging and (config.audit_logging["enabled"] or log_switch):
                    audit_logger.setLevel(logging.INFO)

                    if "log_file" in config.audit_logging:
                        audit_file_handler = RotatingFileHandler(
                            filename=config.audit_logging["log_file"]["name"],
                            maxBytes=10485760,  # 10 MByte
                            backupCount=3,
                        )

                        audit_file_handler.setFormatter(
                            logging.Formatter(
                                fmt="%(asctime)s - AUDIT - %(filename)s:%(lineno)d: %(message)s"
                            )
                        )

                        audit_logger.addHandler(audit_file_handler)

                    if "log_syslog" in config.audit_logging:
                        audit_syslog_handler = SysLogHandler(
                            address=(
                                config.audit_logging["log_syslog"]["host"],
                                int(config.audit_logging["log_syslog"]["port"]),
                            ),
                            facility=LOG_AUTH,
                            socktype=socket.SOCK_STREAM
                            if config.audit_logging["log_syslog"]["protocol"] == "TCP"
                            else socket.SOCK_DGRAM,
                        )

                        audit_syslog_handler.setFormatter(SysLogFormatter(LOG_AUTH))

                        audit_logger.addHandler(audit_syslog_handler)

                else:
                    audit_logger.disabled = True

    @staticmethod
    def audit(message: str) -> None:
        """
        Create an audit log message
        """

        audit_logger.info(message)


logger.audit = Log.audit  # type: ignore
