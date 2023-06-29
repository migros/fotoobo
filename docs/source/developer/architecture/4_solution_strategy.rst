.. Chapter four according to https://arc42.org/overview

.. _SolutionStrategy:

4. Solution Strategy
====================

**fotoobo** should be a flexible "ToolBox" where you can easily add new tools and functionality.
Furthermore, **fotoobo** should have a flexible output system that supports printing data to the
console, rendering files (local or remote) or even sending messages about a job by email.


Core building blocks
--------------------

To honor these design goals, **fotoobo** consists of the following parts:

- The **Fortinet-Library** which allows to interact with the respective Fortinet devices. This
  means basically handling authentication and making REST calls.
- The **Inventory** provides a way to conveniently store information about the devices in YAML-
  files.
- **Tools** are the base building blocks that wrap a functionality of fotoobo, like getting the
  version of the devices or receiving a configuration backup.
- **Frontends** (currently only CLI) provide a way to interact with the tools: transform the
  parameters given in the respective format and render the output back to a format understandable
  by the respective technology/interface.
- **Helpers** provide some commonly used functionality throughout fotoobo like result handling of
  the tools or configuration handling.


Decoupling of the building blocks
---------------------------------

These building blocks are meant to be decoupled as much as possible to allow for easy extension in
the following directions:

- Add new **tools**: These are single functions per use case that accept the required input as
  parameters and render the result into a `Result` object.
- Add new **frontends**: Through decoupling of any input and output with well defined function
  parameters and a `Result` class, fotoobo should be adaptable to new interfaces easily and provide
  full flexibility on how to render the output (data, messages generated during processing, ...) to
  any requested output format (RAW json, beautiful console output, any format using Jinja2).
- Add new **Fortinet devices**: Adding of new Fortinet devices is possible in the Fortinet library.
  Similarities between the device types can easily be exploited using inheritance (for example
  share the FortiManager and FortiAnalyzer most of the code).
- Use other **Inventory formats**: For simplicity in development and because there was no
  pre-existing inventory in another format, fotoobo has developed its own inventory format.
  But in the wild there exists a multitude of established formats and tools: ansible, nornir or
  Netbox to just name a few. Through the use of a single `Inventory` class in any location using
  data from the inventory it is easy to adapt fotoobo to use another format.


Getting data from the respective devices
----------------------------------------

All of the supported devices provide a REST API. For simplicity this API should be used for any
information that can be got this way and only if an information is not available there fotoobo
may use other information sources to collect the data from.

The functionality to authenticate to the API and do basic API calls should be encapsulated into the
respective per-device class inside the Fortinet-Library. The tools will use this as a building
block to build the required functionality. Doing this the respective per-device class should
abstract the API through the interface as defined in the abstract `Fortinet` class.
