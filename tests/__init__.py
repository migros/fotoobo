"""
The tests module for pytest unit testing

Here we initialize the pytest module. To not fill the logfile or /syslog destination whenever tests
are run the logging will be set to disabled here.
"""

from fotoobo.helpers.log import audit_logger, logger

logger.disabled = True
audit_logger.disabled = True
