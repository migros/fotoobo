.. Describes the prerequisites and installation of fotoobo

.. _import_fotoobo:

Importing fotoobo
=================

Although fotoobo is meant to be used as a CLI application you may also import it into your own 
Python modules. With this you can write your own business logic without changing the fotoobo code
itself.

First install fotoobo as documented in :ref:`usage_getting_started`:

.. code-block:: bash

  pip install fotoobo

After successful installation you may import the desired module into your code. Refer to the 
:ref:`auto_fortinet_classes` to get a list of available module parameters.


Examples
--------

FortiGate
^^^^^^^^^

.. code-block:: python

    from fotoobo import FortiGate
    fgt = FortiGate("<HOSTNAME>", "<TOKEN>", https_port=8443, ssl_verify=False)
    print(fgt.get_version())

FortiManager
^^^^^^^^^^^^

.. code-block:: python

    from fotoobo import FortiManager
    fmg = FortiManager("<HOSTNAME>", "<USERNAME>", "<PASSWORD>", ssl_verify=False)
    print(fmg.get_version())
    fmg.logout()

FortiAnalyzer
^^^^^^^^^^^^^

.. code-block:: python

    from fotoobo import FortiAnalyzer
    faz = FortiAnalyzer("<HOSTNAME>", "<USERNAME>", "<PASSWORD>", ssl_verify=False)
    print(faz.get_version())
    faz.logout()

FortiClient EMS
^^^^^^^^^^^^^^^

.. code-block:: python

    from fotoobo import FortiClientEMS
    ems = FortiClientEMS("<HOSTNAME>", "<USERNAME>", "<PASSWORD>", ssl_verify=False)
    ems.login()
    print(ems.get_version())
    ems.logout()

