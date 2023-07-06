.. Describes how to use the FortiGate configuration check

.. _how_to_fortigate_config_check:

The FortiGate Configuration Check
=================================


The FortiGate configuration check module let's you check the configuration of a FortiGate.

If a file is given it checks this file. If you pass a directory, it will do the checks for all the
.conf files in this directory. Exciting, isn't it?

To have a good understanding on how fotoobo handles FortiGate configurations have a look at the
`README <https://github.com/migros/fotoobo/blob/main/README.md>`_.


Usage
-----

``fotoobo fgt confcheck [configuration] [check_bundle]``

Arguments to pass:

- **configuration**: FortiGate configuration object (file or directory)
- **check_bundle**: Fortigate check bundle (file)


Check Bundles
-------------

A check bundle contains one ore more checks that are logically related to each other. These checks
are defined by the individual fields for each entry in *checks*.

This section contains all check bundles which have been implemented in fotoobo,
you can incorporate them in your own bundles.

Note that you need one or more saved FortiGate configuration files to run these check against.

General Bundle Options
^^^^^^^^^^^^^^^^^^^^^^

Check bundles are written in `YAML <https://yaml.org/>`_ files. Each bundle consists of these options:

- **checks**: The checks to perform. See examples.
- **filter-config**: Only perform the check if this config filter matches. As key you may give the
  configuration path. If the value at given path matches the check is executed. (It seems it doesn't
  work if scope is *vdom* :-()
- **filter-info**: Only perform the check if the config information matches. As key you may give a
  key from configuration.info. If the value matches the check is executed. I may prefix the value 
  with '<' or '>'
- **name**: (optional) this is the name of the check. If a name is given it is written to the
  results message so that it's easier to associate the results with the check bundle.
- **path**: The configuration path to check.
- **scope**: Whether to check the global or a vdom configuration. You can only set it to *global* or
   *vdom*.
- **type**: This is the type of check to perform. The available checks are explained below in the
  section *Check Types*.


Check Types
-----------

- count
- exist
- value
- value_in_list


count
^^^^^

This generic bundle checks the count of configuration parts in a configuration list. Use the
following option in *checks*:

- **lt**: less than
- **eq**: equal to
- **gt**: greater that

Of course you can combine these options but it it only makes sense with *lt* and *gt*.

.. code-block:: yaml

    - type: count
      name: <name>
      scope: <global or vdom>
      path: <path>
      filter-info:
        os_version: ">6.2.0"
      checks: 
        <comparing options>

**example**

..  code-block:: yaml

    - type: count
      name: check_1
      scope: global
      path: /system/ntp/ntp-server
      checks: 
        gt: 1
        lt: 11

exist
^^^^^

This is a generic bundle which checks the presence of given configuration options. In *checks* you
may check if a key is present in the configuration with *true* or if it is not present with *false*.
Normally you would use this check with *false* to see if a configuration option is not present
(it's set to default). 

..  code-block:: yaml

    - type: exist
      name: <name>
      scope: <global or vdom>
      path: <path>
      checks: 
        <keys to check with true or false>

**example**

..  code-block:: yaml

    - type: exist
      name: check_1
      scope: global
      path: /system/global
      filter-config:
        /system/ha/mode: a-p
      checks: 
        admin-scp: true
        admintimeout: false


value
^^^^^

This is a generic bundle which checks the presence and value of given configuration options. For the
check to be successful the key MUST be present AND the value must match. Do not use this check to
verify if a configuration option is default. Use *exist* with *false* instead as default
configuration options are not written to the configuration.

- **ignore_missing**: If you wish to ignore a missing configuration add the *ignore_missing* flag
  and set it to *True*. This can be useful if the configuration option to check is not present on
  every FortiGate model.

..  code-block:: yaml

    - type: value
      name: <name>
      scope: <global or vdom>
      path: <path>
      ignore_missing: <bool>
      checks: 
        <key value pairs to check>

**example**

..  code-block:: yaml

    - type: value
      name: check_1
      scope: global
      path: /system/global
      checks: 
        admin-scp: enable
        admintimeout: 60


value_in_list
^^^^^^^^^^^^^

This is a generic bundle which checks the presence and value of given configuration options in a
configuration list. For the check to be successful the key MUST be present in any list item AND the
value must match.

Special options are:

- **inverse**: set *inverse* to search for non matching values

..  code-block:: yaml

    - type: value_in_list
      name: <name>
      scope: <global or vdom>
      path: <path>
      inverse: <bool, default:false>
      checks: 
        <key value pairs to check>

**example**

..  code-block:: yaml

    - type: value
      name: check_1
      scope: global
      path: /system/session-helper
      inverse: true
      checks: 
        name: sip
