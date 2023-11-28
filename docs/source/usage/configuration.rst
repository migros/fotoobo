.. Describes the configuration of fotoobo

.. _usage_configuration:

Configuring fotoobo
===================

Introduction
------------

fotoobo.yaml
^^^^^^^^^^^^

**fotoobo** reads its configuration from a global configuration file, usually named `fotoobo.yaml`.
If you do not explicitly set a file (with the command line option `-c` ) **fotoobo** searches at the
following locations for a file named `fotoobo.yaml` (in the order given here):

1. In the current working directory
2. In `$HOME/.config/`

It will take the first file given and stop searching for other files.

If you do not specify a configuration file and **fotoobo** does not find it in the local directory
it runs with default settings which are referenced below.

The file `fotoobo.yaml.sample`_ provides a skeleton of a `fotoobo.yaml` configuration with all
possible options and the respective documentation for it. Use this as a starting point for your own
configuration.

.. _fotoobo.yaml.sample: https://github.com/migros/fotoobo/blob/main/fotoobo.yaml.sample


CLI-Options
^^^^^^^^^^^

Always keep in mind that the cli options take precedence over the global configuration options. So,
even if there is a global configuration file you may override some of the settings in it with cli
options.

The following list of options are in alphabetical order. In the configuration file the order of the
options does not matter, even if there are dependencies between them.

Note that you can have many basic settings changed by CLI-options, but some more advanced things
like audit logging to a syslog server can only be achieved by using file based configuration.


Settings Reference
------------------

General Settings
^^^^^^^^^^^^^^^^

inventory
"""""""""

*default: "inventory.yaml"*

The **path** and/or **filename** of the :ref:`usage_inventory`. If **fotoobo** needs to connect to a
Fortinet device it loads the needed configuration from this inventory. If you omit the path
**fotoobo** will search in the current working directory.

no_logo
"""""""

*default: false*

Suppress the output of the **fotoobo** logo at the beginning of the execution. Set this value to
``True`` to suppress the logo.

.. _logging:

Logging
^^^^^^^

NOTE: The settings here apply the same to normal logging and audit logging.

If you configure a logging setting it is automatically enabled. Otherwise defaut logging will be
used. Default logging is set to log to **console** with log-level **WARNING**.

.. _logging_level:

level
"""""

*default: "WARNING"*

Choose one of the following log levels for logging: **CRITICAL**, **ERROR**, **WARNING**, **INFO**,
**DEBUG**. This option is not case sensitive, so it also works if you set it to **warning** instead
of **WARNING**.

log_console
"""""""""""

*default: enabled*

Whether **fotoobo** should print all logs to console or not. Defaults to **yes**.
To disable console logging comment out this line using a ``#``.

log_file
""""""""

*default: enabled*

The sup-option ``name`` holds the **path** and/or **filename** where **fotoobo** writes the logfile
to. If you set a log file the logs are appended to a file if the file already exists. If you omit
the path the current working directory is used.

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
Uncomment the line and point it to your ``logging.config`` file to have the custom logging
configuration take effect.

NOTE:
  * If this settings is set, all the above will be ignored.
  * If this settings is set, the audit logging too must be configured in the custom logging config.
    Mixing logging configurations from ``fotoobo.yaml`` and a custom ``logging.config`` is not
    supported.

.. _logging.config.sample: https://github.com/migros/fotoobo/blob/main/logging-config.yaml.sample


Audit-Logging
^^^^^^^^^^^^^

**fotoobo** can produce audit log trails (usually this is just which user called what **fotoobo**
command line from which host when).

The configuration options work the same as described in :ref:`logging`.

NOTE:
  * If :ref:`log_configuration_file` is set, the settings of this part has no effect and you MUST
    configure audit logging in the :ref:`log_configuration_file` too.


.. _vault_service:

Hashicorp Vault Service
^^^^^^^^^^^^^^^^^^^^^^^

For security reasons it may not be safe enough to store sensitive data like credentials and tokens
directly in the **fotoobo** inventory file. Instead the
`Hashicorp Vault <https://www.vaultproject.io/>`_ service may be used to store such data. 
In the **fotoobo** inventory file you may use ``VAULT`` as a placeholder for any attribute. 

The Vault client in **fotoobo** will use the 
`approle <https://developer.hashicorp.com/vault/docs/auth/approle>`_ login to get the data.

The data stored in the Vault service has to be a dictionary which reflects the structure of the
**fotoobo** inventory and its attributes. **fotoobo** will replace all attributes that have the
value ``VAULT`` with the value stored in the vault dictionary.

**Example** 

.. code-block:: yaml
  :caption: An example inventory file

  fortigate-demo:
    hostname: fortigate.local
    token: VAULT
    type: fortigate

  fortimanager-demo:
    hostname: fortimanager.local
    username: demo
    password: VAULT
    type: fortimanager 

.. code-block::
  :caption: Data structure in the Vault servcie

  {
    "fortigate-demo": {
      "token": "your-secret-token"
    },
    "fortimanager-demo": {
      "password": "your-secret-password"
    }
  }

The following configuration options are to be set under a settings group called ``vault``. If you
omit the whole ``vault`` section, the use of the Hashicorp Vault service is disabled (default).

url
"""

The Hashicorp Vault Service URL in the form ``https://vault.local``

namespace
"""""""""

The Namespace to access

data_path
"""""""""

The path in the Vault service where the sensitive data is stored. The data has to be a dictionary
which reflects the structure of the **fotoobo** inventory and its attributes.

role_id
"""""""

The approle role_id

Instead of storing the role_id in the yaml configuration file you may use the system environment
variable ``FOTOOBO_VAULT_ROLE_ID`` to store that value. The environment variable takes precedence
over the configuration file should both be defined.

secret_id
"""""""""

The approle secret_id

Instead of storing the secret_id in the yaml configuration file you may use the system environment
variable ``FOTOOBO_VAULT_SECRET_ID`` to store that value. The environment variable takes precedence
over the configuration file should both be defined.


token_file (optional)
"""""""""""""""""""""

The file to cache the vault token. If you omit this cache file the Vault client will always
relogin with ``role_id`` and ``secret_id`` to get a valid token.
If a cached token is expired or about to expire the Vault client will automatically login and get a
new token.



Example configuration
---------------------

.. literalinclude:: ../../../fotoobo.yaml.sample
    :language: YAML
