.. Describes how to do code

.. _how_to_code:

How To Code
===========

Before you start contributing in this project please read and accept our :ref:`C4`.

Before you start coding always remember the *Zen of Python* by Tim Peters. If you don't know it just
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


Type checking
-------------

Use `Mypy <https://mypy.readthedocs.io/>`_ for static type checking. Always annotate your types.
Mypy will remind you if you accidentally forget it. Because we annotate our types we do not add the
types again in any docstrings.


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
