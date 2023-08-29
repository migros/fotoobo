.. Describes how the FortiGate configuration structure looks like

.. _how_to_fortigate_config:

The FortiGate Configuration Structure
=====================================


Structure
---------

The FortiGate configuration used in **fotoobo** uses a generic structure independent of the VDOM
mode your FortiGate uses. The structure is saved in JSON format and used as a native Python object.
This way you can access every configuration leaf by giving it's path.

Every configuration data structure has a global part where non VDOM relevant configuration is
stored. All VDOM configuration is in the vdom part of the data structure. If you use a FortiGate
without VDOMs the vdom part is always root.

VDOM Mode
---------

The VDOM mode used is determined by analyzing the first comment line in the configuration. There
we'll find the string ``vdom=`` which indicates the mode:

- ``vdom=0``: VDOM mode disabled
- ``vdom=1``: VDOM mode enabled

Meta information
----------------

Every configuration data structure may also hold some meta information for the FortiGate. E.g. its
model or version number. This meta information may be used in filters. 

Examples
--------

The following examples are not realistic as they only show parts of a configuration which is not
able to run. But you should get it.

A FortiGate without VDOM mode enabled
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The FortiGate configuration ...

..  code-block:: text

    #config-version=FGVM64-6.4.5-FW-build1828-210217:opmode=0:vdom=0:user=myuser
    #conf_file_ver=1111
    #buildno=1828
    #global_vdom=1
    config system global
        set admintimeout 60
        set hostname "my-fortigate"
    end
    config router static
        edit 1
            set gateway 10.0.0.1
            set device "port1"
        next
    end

... would be converted into ...

..  code-block:: json

    {
        "vdom": {
            "root": {
                "router": {
                    "static": [
                        {
                            "gateway": "10.0.0.1",
                            "device": "port1",
                            "id": 1
                        }
                    ]
                }
            }
        },
        "global": {
            "system": {
                "global": {
                    "admintimeout": "60",
                    "hostname": "my-fortigate"
                }
            }
        }
    }



A FortiGate with VDOM mode enabled
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The FortiGate configuration ...


..  code-block:: text

    #config-version=FGVM64-6.4.5-FW-build1828-210217:opmode=0:vdom=1:user=myuser
    #conf_file_ver=1111
    #buildno=1828
    #global_vdom=1

    config vdom
    edit root
    next
    edit myvdom
    next
    end

    config global
    config system global
        set admintimeout 60
        set hostname "my-fortigate"
    end

    config vdom
    edit myvdom
    config router static
        edit 1
            set gateway 10.0.0.1
            set device "port1"
        next
    end
    end

... would be converted to ...

..  code-block:: json

    {
        "vdom": {
            "myvdom": {
                "router": {
                    "static": [
                        {
                            "gateway": "10.0.0.1",
                            "device": "port1",
                            "id": 1
                        }
                    ]
                }
            },
            "root": {
            }
        },
        "global": {
            "system": {
                "global": {
                    "admintimeout": "60",
                    "hostname": "my-fortigate"
                }
            }
        }
    }

