.. Describes how to do code

.. _how_to_code:

How To Code
===========

Before you start contributing in this project please read and accept our :ref:`C4`.

Before you start coding always remember the `Zen of Python <https://peps.python.org/pep-0020/>`_ by Tim Peters. If you don't know it just
type :code:`import this` in an interactive Python interpreter.

We strongly encourage you to use any Linux environment to code. WSL on Windows is also possible. The
project was never tested on a native Windows system.


Package Management
------------------

Use `Poetry <https://python-poetry.org/>`_ for package management.


Code Style
----------

-   We try to follow the
    `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html>`_. Exceptions to this
    guideline are documented below.

-   Use a formatter (we suggest `Black <https://github.com/psf/black>`_) to comply with our styling
    guidelines.

-   Use a linter (we suggest `pylint <https://github.com/pylint-dev/pylint>`_) for static code
    analysis.

These styles are enforced by a tox pipeline running pylint and black that also runs on every pull
request on GitHub.

**Line length**

Maximum line length is 100 characters.

**Docstrings**

Use docstrings for every module, function or method. We refer to `PEP 257 <https://peps.python.org/pep-0257/>`_ with following additions:

- The tripple quotes (""") are always on a separate line. Even for one-line docstrings.
- Docstrings must contain full sentences ending with a period.
- There is always a blank line after a docstring.
- Doctrings are allowed to span over the full line lenght of 100 characters.

**Good Example**

..  code-block:: python

    def good() -> str:
        """
        This is a good example of a docstring.

        This function simply returns a word and does nothing else. It is just here for demonstation
        purposes and has no productive effect. Just ignore it.
        """

        return "Good"

**Bad Example**

..  code-block:: python

    def bad() -> str:
        """bad example
        This function simply returns a word and does nothing else. It is just here for demonstation
        purposes and has no productive effect. ignore it"""
        return "Bad"


Type checking
-------------

Use `Mypy <https://mypy.readthedocs.io/>`_ for static type checking. Always annotate your types.
Mypy will remind you if you accidentally forget it. Because we annotate our types we do not add the
types again in any docstrings.

**Good Example**

..  code-block:: python

    from typing import Any

    def good(a: int, b: int, c: dict[str, Any]) -> str:
        """
        This is a good example.

        Args:
            a: A number
            b: Another number
            c: A dictionary containing stuff of different types

        Returns:
            The sum of the two numbers a and b as string
        """

        # do something
        some_weird_object = WeirdClass(c)  # type: ignore
        # do more things

        return str(a + b)

**Bad Example**

..  code-block:: python

    def bad(a, b):
        """
        This is a bad example.

        Args:
            a (int): A number
            b (int): Another number

        Returns:
            (str) The sum of the two numbers
        """
        
        return str(a + b)

If it gets too complicated you're allowed to use ``# type: ignore`` or type ``Any`` but use it rarely and with caution.

Testing
-------

Use `Pytest <https://docs.pytest.org/>`_ for code testing and test coverage measurement. We seek a
coverage of at least 90%. You'll find more detailed information about writing tests in our
:ref:`how_to_test` documentation.

Test Automation
---------------

Use `Tox <https://tox.wiki/en/latest/>`_ for test automation. Whenever you did some changes you wish
to publish run :code:`tox` before any merge request. Every merge request which does not pass all
tests will be rejected.

Release
-------

Periodically the maintainers decide to create a new release. If you did some breaking changes which
are worth a new release just ask one of them. The process is documented in our :ref:`how_to_release`
documentation.
