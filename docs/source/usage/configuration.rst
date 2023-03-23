.. Describes the configuration of fotoobo

.. _usage_configuration:

Configuring fotoobo
===================

Introduction
------------

fotoobo.yaml
^^^^^^^^^^^^

fotoobo reads its configuration from a global configuration file, usually named `fotoobo.yaml`. If
you do not explicitly set a file (with the command line option `-c` ) fotoobo searches at the following
locations for a file named `fotoobo.yaml` (in the order given here):

1. In the current working directory.
2. In `$HOME/.config/`

It will take the first file given and stop searching for other files.

If you do not specify a configuration file and fotoobo does not find it in the local directory it
runs with default settings which are referenced below.

The file `fotoobo.yaml.sample`_ provides a skeleton of a `fotoobo.yaml` configuration with all
possible options and the respective documentation for it. Use this as a starting point for your own
configuration.

.. _fotoobo.yaml.sample: https://github.com/migros/fotoobo/blob/main/fotoobo.yaml.sample


CLI-Options
^^^^^^^^^^^

Always keep in mind that the cli options take precedence over the global configuration options. So,
even if there is a global configuration file you may override some of the settings in it with cli
options.

The following list of options are in alphabetical order. In the configuration file the order of the options
does not matter, even if there are dependencies between them.

Note that you can have many basic settings changed by CLI-options, but some more advanced things like audit
logging to a syslog server can only be achieved by using file based configuration.


Settings Reference
------------------

General Settings
^^^^^^^^^^^^^^^^

backup_dir
""""""""""

*default: None*

The **path** for the FortiGate backup files. This setting is mandatory if using ``fotoobo fgt backup``.

inventory
"""""""""

*default: "inventory.yaml"*

The **path** and/or **filename** of the :ref:`usage_inventory`. If fotoobo needs to connect to a Fortinet device it
loads the needed configuration from this inventory. If you omit the path ``fotoobo`` will search in the
current working directory.

no_logo
"""""""

*default: false*

Suppress the output of the fotoobo logo at the beginning of the execution. Set this value to ``True`` to
suppress the logo.

snmp_community
""""""""""""""

*default: ""*

The SNMPv2 community string to use to connect to the Fortinet assets (used for examples by commands
``fotoobo ...``. By now it's only supported to have one single community string for all devices,
so make sure you configure the same string on every device. Also SNMPv2 is the only supported SNMP
version at the moment.

.. _logging:

Logging
^^^^^^^

NOTE: The settings here apply the same to normal logging and audit logging.

.. _logging_enabled:

enabled
"""""""

*default: false*

Set this value to **true** or **false** to enable or disable all logging. Of course after setting
``enabled`` to **false** the option :ref:`logging_level` has no effect anymore.

.. _logging_level:

level
"""""

*default: "INFO"*

Choose one of the following log levels for logging: **CRITICAL**, **ERROR**, **WARNING**, **INFO**, **DEBUG**.
This option is not case sensitive, so it also works if you set it to **warning** instead of **WARNING**.
If the option :ref:`logging_enabled` is set to **false** this option does not have any effect.


log_console
"""""""""""

*default: enabled*

Whether fotoobo should print all logs to console or not. Defaults to **yes** (if logging is :ref:`logging_enabled`).
To disable console logging comment out this line using a ``#``.


log_file
""""""""

*default: enabled*

The sup-option ``name`` holds the **path** and/or **filename** where ``fotoobo`` writes the logfile to (if logging
is :ref:`logging_enabled`). If you set a log file the logs are appended to a file if the file already exists. If
you omit the path the current working directory is used.

If you want to disable file logging, comment the respective lines out using a ``#``.

log_syslog
""""""""""

*default: disabled (commented out)*

The configuration to log to syslog. If you need this, remove the comment values (``#``) and set the
values of ``host``, ``port`` and ``protocol`` to the correct values.

.. _log_configuration_file:

log_configuration_file
""""""""""""""""""""""

*default: disabled (commented out)*

If you want to fine tune logging even more, you can provide an own python logging configuration
file. There is a `logging.config.sample`_ where you can find more information about this.
Uncomment the line and point it to your ``logging.config`` -file to have the custom logging
configuration take effect.

NOTE:
  * If this settings is set, all the above (including :ref:`logging_enabled`) will be ignored.
  * If this settings is set, the audit logging too must be configured in the custom logging config.
    Mixing logging configurations from ``fotoobo.yaml`` and a custom ``logging.config`` is not
    supported.

.. _logging.config.sample: https://github.com/migros/fotoobo/blob/main/logging-config.yaml.sample


Audit-Logging
^^^^^^^^^^^^^

fotoobo can produce audit log trails (usually this is just which user called what fotoobo command
line from which host when).

The configuration options work the same as described in :ref:`logging`.

NOTE:
  * If :ref:`log_configuration_file` is set, the settings of this part has no effect and you MUST
    configure audit logging in the :ref:`log_configuration_file` too.


Example configuration
---------------------

.. literalinclude:: ../../../fotoobo.yaml.sample
    :language: YAML
