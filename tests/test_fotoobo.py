"""
Test fotoobo
"""

import re

from fotoobo import __version__
from fotoobo.main import main


def test_version() -> None:
    """
    Testing the fotoobo version

    The RegEx used for testing the semantic version string is very simplified here but it is
    enough for fotoobo.
    Detailed information on RegEx testing semantic versions can be found here:
    https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
    """
    assert re.search(r"^[0-9]+\.[0-9]+\.[0-9]+", __version__)


def test_main() -> None:
    """
    Calling the main() function directly has the same effect as calling the cli app without any
    command line arguments. So main() will always exit with sys.exit(2).
    """
    try:
        main()
    except SystemExit as err:
        assert err.args[0] == 2
