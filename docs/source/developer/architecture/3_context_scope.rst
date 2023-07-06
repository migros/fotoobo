.. Chapter three according to https://arc42.org/overview

.. _ContextScope:

3. Context & Scope
==================

Context
-------

**fotoobo** communicates with different Fortinet products on one side and other devices like
SFTP and SMPT servers on the other side.

(Picture)

The main output formats are console or files written to the file system.


Scope
-----

Fortinet products are used worldwide and by large number of companies. There is already a lot of
tooling to support Fortinet devices. **fotoobo** aims to fill a gap in this tooling support and
solve some common tasks in a simple way.

Based on this the scope of **fotoobo** is defined as follows:

- Get, enrich and summarize information from one or more Fortinet product(s), that is otherwise not
  easily available

    - for presentation on console
    - for further use as raw JSON output (for a monitoring system for example)
    - to render any Jinja2 template based on it (for HTML-Reports or config input to other systems
      for example).

- **fotoobo** will basically only *read* from the respective Fortinet devices. Write operations
  should be done with the `Fortinet ansible Module <https://docs.ansible.com/ansible/latest/collections/fortinet/index.html>`_
  or by using custom scripts.


