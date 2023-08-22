.. Chapter four according to https://arc42.org/overview

.. _SolutionStrategy:

4. Solution Strategy
====================

Design Goals
------------

**fotoobo** is meant to be a flexible "tool box" where you can easily add new tools and
functionality. Furthermore, **fotoobo** should have a flexible output system that supports printing
data to the console, rendering files (local or remote) or even sending results of a command by
email.


Core building blocks
--------------------

To honor these design goals, **fotoobo** consists of the following parts:

- The **Fortinet-Library** which allows to interact with the respective Fortinet devices. This
  means basically handling authentication and making REST calls (folder :code:`fotoobo/fortinet`).
- The **Inventory** provides a way to conveniently store information about the devices in YAML-
  files (folder :code:`fotoobo/inventory`).
- **Tools** are the base building blocks that wrap a functionality of **fotoobo**, like getting the
  version of the devices or receiving a configuration backup (folder :code:`fotoobo/tools`).
- **Frontends** (currently only CLI) provide a way to interact with the tools: transform the
  parameters given in the respective format and render the output back to a format understandable
  by the respective technology/interface (folder :code:`fotoobo/cli`).
- **Helpers** provide some commonly used functionality throughout **fotoobo** like result handling
  of the tools or configuration handling (folder :code:`fotoobo/helpers`).


Decoupling of the building blocks
---------------------------------

These building blocks are meant to be decoupled as much as possible to allow for easy extension in
the following directions:

- Add new **tools**: These are single functions or methods per use case that accept the required
  input as parameters and render the result into a `Result` object.
- Add new **frontends**: Through decoupling of any input and output with well defined function
  parameters and a `Result` class, **fotoobo** should be easily adaptable to new interfaces and
  provide full flexibility on how to render the output (data, messages generated during processing,
  ...) to any requested output format (RAW json, beautiful console output, any format using Jinja2).
- Add new **Fortinet devices**: Adding of new Fortinet devices is possible in the Fortinet library.
  Similarities between the device types can easily be exploited using inheritance (for example
  the FortiManager and FortiAnalyzer share most of the code).
- Use other **Inventory formats**: For simplicity in development and because there was no
  pre-existing inventory in another format, **fotoobo** has developed its own inventory format.
  But in the wild there exists a multitude of established formats and tools: ansible, nornir or
  Netbox to just name a few. Through the use of a single `Inventory` class in any location using
  data from the inventory it is easy to adapt **fotoobo** to use another format.


Getting data from the respective devices
----------------------------------------

All of the supported devices provide a REST API. For simplicity this API should be used for any
information that can be got this way. Only if an information is not available through this
API **fotoobo** should use other information sources like SNMP or SSH to collect the data from.

The functionality to authenticate to the API and do basic API calls should be encapsulated into the
respective per-device class inside the Fortinet-Library. The tools will use this as a building
block to build the required functionality. Doing this the respective per-device class should
abstract the API through the interface as defined in the abstract `Fortinet` class.


Used Frameworks
---------------

To build **fotoobo** we use the following frameworks.

Runtime Requirements
^^^^^^^^^^^^^^^^^^^^

- `Python <https://www.python.org/>`_ 3.8+ (all stable versions from this on will be checked in the
  integration pipeline on GitHub).

   - *NOTE: The supported Python versions are based on the Python versions shipped with some of the
     major Linux distributions' LTS editions.*

- `requests <https://requests.readthedocs.io/en/latest/>`_ to interact with the REST APIs.
- `Typer <https://typer.tiangolo.com/>`_ to create the CLI frontend.
- `Rich <https://rich.readthedocs.io/en/stable/>`_ to enhance the CLI output.
- `PyYAML <https://pyyaml.org/wiki/PyYAML>`_ for reading and writing YAML files.
- `Jinja2 <https://palletsprojects.com/p/jinja/>`_ for rendering templates.


For Development
^^^^^^^^^^^^^^^

- `Tox <https://tox.wiki/en>`_ to simplify and automate the whole quality assurance part.
- `Black <https://black.readthedocs.io/en/stable/>`_ for consistent code formatting.
- `isort <https://pycqa.github.io/isort/>`_ for consistent import sorting.
- `Pylint <https://pypi.org/project/pylint/>`_ for static code analysis.
- `MyPy <https://www.mypy-lang.org/>`_ for static type checking.
- `pytest <https://docs.pytest.org/>`_ for driving and running all the code tests.
- `pytest-cov <https://github.com/pytest-dev/pytest-cov>`_ for generating test coverage reports.
- `Sphinx <https://www.sphinx-doc.org/>`_ for generating the documentation.
- `pygount <https://github.com/roskakori/pygount>`_ for statistics about written code lines.
