.. Here we document the fotoobo inventory file format

.. _usage_inventory:

The fotoobo inventory
=====================

Any device you want to access needs to be defined in the **fotoobo** inventory. The path to this
inventory you have to set in the :ref:`global configuration<usage_configuration>`. From there
**fotoobo** reads all the information about the devices to use during operation. Even if you may
name it whatever you want it's best practice to name it *inventory.yaml*.


Important Security Consideration
--------------------------------

The **fotoobo** inventory is a `yaml file <https://yaml.org/>`_ containing your Fortinet and other 
devices. It is used to connect to these devices. Every device is listed with its name and the 
required connection parameters. This also means secret access keys for the devices, so make sure it
is never exposed to unauthorized individuals. Usually this means you need to make sure that the
inventory is...

1. only stored on the host you want to run **fotoobo** (never checked into a git repository, ...)
2. only readable to the user that runs **fotoobo** (and there is absolutely no reason that this user
   is root!)

`Don't say I didn't tell you <https://www.youtube.com/watch?v=1bVy1sLVasY>`_.

To make the handling of sensitive data a bit safer you may store such data in a Hashicorp Vault
service. To do so you just give your sensitive attributes the value ``VAULT`` and **fotoobo** will
lookup them in the Vault service. To configure your Hashicorp Vault access, have a look at
:ref:`global configuration<vault_service>`


fotoobo Inventory Basics
------------------------

The entry for each device begins with its name which can be used in the **fotoobo** cli to access
it.

Beneath the simple device information it may also contain global configuration for every type of
device. The section which holds the global configuration is named ``globals`` so make sure you
haven't any device with the same name.

**Simple Example**

.. code-block:: yaml

  globals:
    fortigate:
      https_port: 4443
    fortimanager:
      ssl_verify: false
  my-fortigate1:
    hostname: myfortigate1.local:
    token: the_api_key_from_the_device
    type: fortigate
  my-fortigate2:
    hostname: myfortigate2.local
    https_port: 8443
    token: the_api_key_from_the_device
    type: fortigate
  my-fortimanager:
    hostname: myfortimanager.local
    username: the_fortimanager_username
    password: the_fortimanager_password
    session_path: "path/to/session/file"
    type: fortimanager


**fotoobo cli example**

.. code-block:: bash

  fotoobo fgt get version my-fortigate1

Devices may have the following options depending of their device type:


Globals
-------

Define your devices global configuration by device type. The possible key value pairs to configure
may depend on the type of the device. See the respective device type below for available options.
These options may be overwritten on any particular device.

**example**

.. code-block:: yaml

  globals:
    fortigate:
      https_port: 4443
    fortimanager:
      ssl_verify: "/path/to/custonm/ca.pem"


FortiGate Devices
-----------------

To connect to FortiGate devices you do not login with a username and password. Instead you submit
an API access token in every request.

**hostname** *string* (required)

  The hostname or IP address of the FortiGate device. Do not add the protocol before or the port
  number after, just the hostname or ip address. Due to security reasons the connection to a
  FortiGate is always done with the protocol https.

  * ``myfortigate1.mydomain.local``
  * ``10.20.30.40``

**https_port** *number* (optional, default 443)

  The port number to use for accessing the https api.

**ssl_verify** *bool | string* (optional, default: true)

  Check host SSL certificate (true) or not (false). You can also provide a path to a custom
  CA certificate or CA bundle. Please be aware that disabling SSL certificate
  verification is a security risk and should not be used in a production environment.
  
**token** *string* (required)

  The API access token from the FortiGate. Please read the
  `FortiOS documentation <https://docs.fortinet.com/product/fortigate/>`_ for learning how to
  create an API access token.

**type** *string* (required)

  Specifies the type of device. Use 'fortigate' for FortiGate devices. It is used if **fotoobo** has
  to search for specific types of devices, e.g. when it should iterate over all FortiGate devices in
  the inventory.

**example**

.. code-block:: yaml

  myfortigate1:
    hostname: fortigate-test.mydomain.local
    https_port: 4443
    ssl_verify: false
    token: 2d85x75cv_example_4wl6ns7xd4o
    type: fortigate


FortiManager / FortiAnalyzer Devices
------------------------------------

**hostname** *string* (required)

  The hostname or ip address of the FortiManager or FortiAnalyzer device. Do not add the protocol
  before or the port number after, just the hostname or ip address. Due to security reasons the
  connection to a FortiManager or FortiAnalyzer is always done with the protocol https.

  * ``myfortimanager.mydomain.local``
  * ``myfortianalyzer.mydomain.local``
  * ``10.20.30.40``

**https_port** *number* (optional, default 443)

  The port number to use for accessing the https api.

**password** *string* (required)

  The password used to login to the FortiManager or FortiAnalyzer device.

**session_path**

  Use this option to specify a directory where the session key should be stored. The name of the
  file will be generated from the hostname. During login to FortiManager/FortiAnalyzer this session
  key is used if the file exists.
  If you omit this option the session key store feature is disabled and every login to
  FortiManager/FortiClient is done with its username and password.

**ssl_verify** *bool | string* (optional, default: true)

  Check host SSL certificate (true) or not (false). You can also provide a path to a custom
  CA certificate or CA bundle. Please be aware that disabling SSL certificate
  verification is a security risk and should not be used in a production environment.

**username** *string* (required)

  The username used to login to the FortiManager or FortiAnalyzer device.

**type** *string* (required)

  Specifies the type of device. Use 'fortimanager' for FortiManager devices or 'fortianalyzer' for
  FortiAnalyzer devices.

**example**

.. code-block:: yaml

  myfortimanager1:
    hostname: fortimanager-test.mydomain.local
    https_port: 4443
    username: myusername
    password: mysupersecurepassword
    session_path: "~/.cache"
    type: fortimanager


FortiClient EMS Devices
-----------------------

**cookie_path** *string* (optional)

  FortiClient EMS does support cookie handling. Use this option to specify a directory where cookies
  should be stored. The name of the cookie will be generated from the hostname. During login to
  FortiClient EMS this cookie is used if it exists. This will make requests much faster.
  If you omit this option the cookie store feature is disabled and every login to FortiClient EMS is
  done with username and password.

**hostname** *string* (required)

  The hostname or IP address of the FortiClient EMS device. Do not add the protocol before or the
  port number after, just the hostname or ip address. Due to security reasons the connection to a
  FortiClient EMS is always done with the protocol https.

  * ``myems.mydomain.local``
  * ``10.20.30.40``

**https_port** *number* (optional, default 443)

  The port number to use for accessing the https api.

**password** *string* (required)

  The password used to login to the FortiClient EMS.

**ssl_verify** *bool | string* (optional, default: true)

  Check host SSL certificate (true) or not (false). You can also provide a path to a custom
  CA certificate or CA bundle. Please be aware that disabling SSL certificate
  verification is a security risk and should not be used in a production environment.

**username** *string* (required)

  The username used to login to the FortiClient EMS.

**type** *string* (required)

  Specifies the type of device. Use 'forticlientems' for FortiClient EMS devices.

**example**

.. code-block:: yaml

  myfortiems1:
    hostname: ems-test.mydomain.local
    https_port: 4443
    username: myusername
    password: mysupersecurepassword
    cookie_path: "/path/to/cookie/dir"
    type: forticlientems


The FortiCloud Asset Management
-------------------------------

Access to the FortiCloud Asset Management API is very similar to a simple device. The only 
speciality is that you have to define the host as *forticloud* with the type of *forticloud*. You 
do not need to specify a *hostname* or *https_port* as it is hardcoded in the module.

**token_path** *string* (optional)

  Use this option to specify a directory where the *access_token* should be stored. The filename of 
  the token file will be *support.fortinet.com.token*. During login to the FortiCloud this token is 
  used if it exists. This will make requests much faster.
  If you omit this option the token store feature is disabled and every login to FortiCloud is done
  with username and password.

**password** *string* (required)

  The password used to login to the FortiClient EMS.

**ssl_verify** *bool | string* (optional, default: true)

  Check host SSL certificate (true) or not (false). You can also provide a path to a custom
  CA certificate or CA bundle. Please be aware that disabling SSL certificate
  verification is a security risk and should not be used in a production environment.

**username** *string* (required)

  The username used to login to the FortiClient EMS.

**type** *string* (required)

  Specifies the type of device. Use 'forticloudasset' for FortiCloud Asset management.

**example**

.. code-block:: yaml

  forticloud:
    username: myusername
    password: mysupersecurepassword
    token_path: "/path/to/token/dir"
    ssl_verify: false
    type: forticloudasset


Generic Devices
---------------

There are several non Fortinet devices you may use within **fotoobo**. They each need different or
additional arguments to initialize.

ftp
^^^

An ftp server may be used to upload configuration backups.

**directory** *string* (required)

  Define the directory on the ftp server in which to upload the data to.

**hostname** *string* (required)

  The hostname or ip address of the desired ftp server.

**protocol** *string* (optional, default: sftp)

  Either 'sftp' or 'ftp', defaults to 'sftp'.

**directory** *string* (required)

  Define the directory on the ftp server in which to upload the data to.

**username** *string* (required)

**password** *string* (required)

  The password used to login to the ftp server.

**type** *string* (optional, default: generic)

  For ftp servers always use 'ftp' as type.

**example**

.. code-block:: yaml

  myftp:
    hostname: ftp.local
    protocol: sftp
    directory: "path/to/files/dir"
    username: username
    password: password
    type: ftp

smtp
^^^^

Define an smtp server to send notifications by mail. Not all utilities support smtp notification.
See the help for information.

**hostname** *string* (required)

  The hostname or ip address of the desired smtp server.

**port** *integer* (optional, default: 25)

  The tcp port on which the smtp server listens for incoming connections.

**recipient** *string* (required)

**sender** *string* (required)

**subject** *string* (required)

**type** *string* (optional, default: generic)

  For smtp servers always use 'smtp' as type.

**example**

.. code-block:: yaml

  mysmtp:
    hostname: smtp.local
    port: 25
    recipient: fotoobo@local
    sender: fotoobo@local
    subject: fotoobo notification
    type: smtp
