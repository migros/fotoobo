.. Describes the prerequisites and installation of fotoobo

.. _import_fotoobo:

Importing fotoobo
=================

Although **fotoobo** is meant to be used as a CLI application you may also import it into your own 
Python modules. With this you can write your own business logic without changing the **fotoobo**
code itself.

First install **fotoobo** as documented in :ref:`usage_getting_started`:

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

Using an inventory file
^^^^^^^^^^^^^^^^^^^^^^^

You can maintain an :ref:`inventory file<usage_inventory>` to load the assets from. This helps not having API tokens or username/passwords directly in the source code.

Imagine you created the inventory file ``~/.config/inventory.yaml``:

.. code-block:: yaml

    fmg-test:
        hostname: myfortimanager.local
        username: the_fortimanager_username
        password: the_fortimanager_password
        type: fortimanager

With this inventory file you can use the asset ```fmg-test`` in your code:

.. code-block:: python

    from fotoobo.inventory import Inventory
    inventory = Inventory(Path("~/.config/inventory.yaml"))
    fmg = inventory.get_item("fmg-test")
    print(fmg.get_version())


Using a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can read your fotoobo :ref:`configuration file<usage_configuration>`. This is useful if you wish to load and change settings like :ref:`inventory file<usage_inventory>`, :ref:`logging options<logging>` or a :ref:`vault configuration<vault_service>`.

Use the inventory file ``~/.config/inventory.yaml`` with the string ``VAULT`` as the toke or password for your assets.

.. code-block:: yaml

    fmg-test:
        hostname: myfortimanager.local
        username: the_fortimanager_username
        password: VAULT
        type: fortimanager

Then you have to specify this inventory file and the vault configuration in the fotoobo configuration file ``~/.config/fotoobo.yaml``.

.. code-block:: yaml

    inventory: ~/.config/inventory.yaml
    vault:
        url: https://vault.local
        namespace: vault_namespace
        data_path: /v1/kv/data/fotoobo
        role_id: ...
        secret_id: ...
        token_file: ~/.cache/token.key

With these preparations you can use the fotoobo configuration to access your assets.

.. code-block:: python

    from fotoobo.helpers.config import config
    from fotoobo.inventory import Inventory
    config.load_configuration()
    config.vault["ssl_verify"] = False
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get_item("fmg-test")
    print(fmg.get_version())
