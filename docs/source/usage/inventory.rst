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

The entry for each device begins with its name which can be used in the fotoobo cli to access it.

**Simple Example**

.. code-block:: yaml

  my-fortigate1:
    hostname: myfortigate1.manage.it:
    token: the_api_key_from_the_device
    type: fortigate
  my-fortigate2:
    hostname: myfortigate2.manage.it:8443
    token: the_api_key_from_the_device
    type: fortigate


**fotoobo cli example**

.. code-block:: bash

  fotoobo fgt get version my-fortigate1

Devices may have the following options depending of their device type:


FortiGate Devices
-----------------

To connect to FortiGate devices you do not login with a username and password. Instead you submit
an API access token in every request.

**hostname** *string* (required)
  The hostname or IP address of the FortiGate device. May be followed by its connection port if
  it's not 443. Due to security reasons the connection to a FortiGate is always done with the
  protocol https.

  * ``myfortigate1.mydomain.local``
  * ``myfortigate1.mydomain.local:8443``
  * ``10.20.30.40:9443``

**ssl_verify** *bool* (optional, default: true)
  Check hosts SSL certificate (true) or not (false). Please be aware that disabling SSL certificate
  verification is a security risk and should not be used in a production environment.
  `Don't say I didn't tell you <https://www.youtube.com/watch?v=1bVy1sLVasY>`_.

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
    hostname: fortigate-test.mydomain.local:9443
    ssl_verify: false
    token: 2d85x75cv_example_4wl6ns7xd4o
    type: fortigate


FortiManager / FortiAnalyzer Devices
------------------------------------

**hostname** *string* (required)
  The hostname or ip address of the FortiManager or FortiAnalyzer device. May be followed by its
  connection port if it's not 443. Due to security reasons the connection to a FortiManager or
  FortiAnalyzer is always done with the protocol https.

  * ``myfortimanager.mydomain.local``
  * ``myfortianalyzer.mydomain.local:8443``
  * ``10.20.30.40:9443``

**password** *string* (required)
  The password used to login to the FortiManager or FortiAnalyzer device.

**username** *string* (required)
  The username used to login to the FortiManager or FortiAnalyzer device.

**type** *string* (required)
  Specifies the type of device. Use 'fortimanager' for FortiManager devices or 'fortianalyzer' for
  FortiAnalyzer devices.

**example**

.. code-block:: yaml

  myfortimanager1:
    hostname: fortimanager-test.mydomain.local:9443
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
  The hostname or IP address of the FortiClient EMS device. May be followed by its connection port
  if it's not 443. Due to security reasons the connection to a FortiClient EMS is always done with
  the protocol https.

  * ``myems.mydomain.local``
  * ``myems.mydomain.local:8443``
  * ``10.20.30.40:9443``

**password** *string* (required)
  The password used to login to the FortiClient EMS.

**username** *string* (required)
  The username used to login to the FortiClient EMS.

**type** *string* (required)
  Specifies the type of device. Use 'forticlientems' for FortiClient EMS devices.

**example**

.. code-block:: yaml

  myfortiems1:
    hostname: ems-test.mydomain.local:9443
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

**password** *string* (required)
  The password used to login to the ftp server.

**type** *string* (optional, default: generic)
  For ftp servers always use 'ftp' as type.

**username** *string* (required)

**example**

.. code-block:: yaml

  myftp:
    hostname: ftp.local
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
