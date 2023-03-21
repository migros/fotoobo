.. Here we document the fotoobo inventory file format

.. _usage_inventory:

The fotoobo inventory
=====================

If you need to access any device you have to define the fotoobo inventory in the
:ref:`global configuration<usage_configuration>`. From there fotoobo reads all the information about
the devices to use during operation. Even if you may name it however you want it's best practice to
name it *inventory.yaml*.

The fotoobo inventory is a `yaml file <https://yaml.org/>`_ containing your Fortinet and other 
devices. It is used to connect to these devices. Every device is listed with its name and the 
required connection parameters. It may also contain secret access keys for the devices so make 
sure it is never exposed to unauthorized individuals.
`Don't say I didn't tell you <https://www.youtube.com/watch?v=1bVy1sLVasY>`_.

The entry for each device begins with its name which can be used in the fotoobo cli to access it.

Beneath the simple device information it may also contain global configuration fer every type of
device. The section which holds the global configuration is named `globals` so make sure you haven't
any device with the same name.

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
      ssl_verify: false


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

**ssl_verify** *bool* (optional, default: true)

  Check hosts SSL certificate (true) or not (false). Please be aware that disabling SSL certificate
  verification is a security risk and should not be used in a production environment.
  
**token** *string* (required)

  The API access token from the FortiGate. Please read the
  `FortiOS documentation <https://docs.fortinet.com/product/fortigate/>`_ for learning how to
  create an API access token.

**type** *string* (required)

  Specifies the type of device. Use 'fortigate' for FortiGate devices. It is used if fotoobo has to
  search for specific types of devices, e.g. when it should iterate over all FortiGate devices in
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

**ssl_verify** *bool* (optional, default: true)

  Check hosts SSL certificate (true) or not (false). Please be aware that disabling SSL certificate
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

**ssl_verify** *bool* (optional, default: true)

  Check hosts SSL certificate (true) or not (false). Please be aware that disabling SSL certificate
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
    cookie_path: data
    type: forticlientems

Generic Devices
---------------

There are several non Fortinet devices you may use within fotoobo. They each need different or
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
    directory: dir1/dir2/
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
