.. Describes the prerequisites and installation of fotoobo

.. _usage_getting_started:

Getting Started
===============

Prerequisites
-------------

This fotoobo package assumes you have

* A Linux environment
* Network access to Fortinet products
* Administrative access to the Fortinet products (username/password, api key, snmp community)
* Fundamental knowledge of what you are doing


Installing fotoobo
------------------

Please install fotoobo on any Linux machine or container with Python on it. Although Python is an os
independent programming language fotoobo is not meant to be installed and is not tested on any
Windows machine. Not yet. If you want to use Windows then run fotoobo in
`WSL <https://learn.microsoft.com/de-de/windows/wsl/>`_.

.. code-block:: bash

  pip install fotoobo


Execution
---------

In its simplest form fotoobo lets you run different predefined functions as a cli application.

Start with:

.. code-block:: bash

  fotoobo --help

An overview of all available fotoobo commands can be shown with:

.. code-block:: bash

  fotoobo get commands


Configuration
-------------

Start by creating a configuration file named `fotoobo.yaml`. At least give it a path to your
inventory.

.. code-block:: yaml

  # The path to the inventory file
  inventory: inventory.yaml

And of course you must also create the inventory file which in this case is called `inventory.yaml`.

.. code-block:: yaml

  demo-fortigate:
    hostname: <YOUR FORTIGATE DNS NAME OR IP-ADDRESS>
    ssl_verify: false
    token: <YOUR FORTIGATE API ACCESS TOKEN>
    type: fortigate

Now you can run fotoobo commands to the configured FortiGate. As an example you can get the FortiOS
version from the FortiGate by issuing the following command:

.. code-block:: bash

  fotoobo fgt get version demo-fortigate

The same way you may access any other supported Fortinet product in your network. Other products
might need other or additional configuration. For detailed information see:

  * :ref:`usage_configuration`
  * :ref:`usage_inventory`

Termination
-----------

fotoobo exits with defined status codes. You can show the status code in bash with ``echo $?``. The
fotoobo status code values are based on the
`levels from the Python logging module <https://docs.python.org/3/library/logging.html#logging-levels>`_.
The cli application (made with `typer <https://typer.tiangolo.com/>`_) exits with its own exit codes
which do not correspond with the Python logging levels.

.. code-block:: bash

  fotoobo$ fotoobo ems get version
  FortiClient EMS version: 1.2.3
  fotoobo$ echo $?
  0

The following status codes are defined and used in fotoobo:


.. list-table::
  :widths: 1 1
  :header-rows: 1

  * - code
    - description
  * - 0
    - normal termination without any error
  * - 2
    - cli termination with error
  * - 30
    - normal termination with warning
  * - 40
    - abnormal termination with error
  * - 50
    - critical termination with exception and traceback

After a critical termination with exit code 50 you may find the traceback information in the file
traceback.log in the local directory.
