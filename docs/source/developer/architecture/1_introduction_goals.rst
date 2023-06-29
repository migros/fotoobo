.. Chapter one according to https://arc42.org/overview

.. _1IntroductionGoals:

1. Introduction and Goals
=========================

**fotoobo** is the mighty **Fo**\ rtinet **too**\l\ **bo**\ x for managing your Fortinet environment.
The tool consists of several useful utilities with functionality which is not covered by the
standard Fortinet management suite. It is meant to be extendable to your needs.

One of its main use cases for the developers has been to give several different scripts a common
home. With this they could apply the DRY principle to them by using a common platform for getting
and pushing data to several Fortinet products.

Goals
-----
- **fotoobo** should simplify managing your Fortinet device zoo by providing some simple to use
  commands for doing daily tasks or gather information for further use, e.g. monitoring.
- It should be easily extendable for further needs.
- It should be easily usable in cron-jobs or custom scripts.
- Fill in gaps and with this do not recreate existing ways of getting data from your Fortinet
  products. This means a bit more precise:

  - Summarize or enhance information that can be got using SNMP or the REST API
  - Create simple, well integrable tools for common tasks: backing up configs, enhance data for
    simpler use in monitoring systems, ...


Supported Fortinet products
---------------------------

At the moment **fotoobo** supports the following Fortinet products:

- FortiGate (tested with FortiOS 6.4, 7.0 and 7.2)
- FortiManager
- FortiClient EMS
- FortiAnalyzer


Core use cases
--------------

Some of **fotoobo**'s main use cases are:

- Backup configurations from FortiGate devices (and push them to an SFTP server)
- Fill in gaps in the monitoring of different Fortinet products (e.g. SSLVPN pool usage when more
  than one IP subnet is available for client IPs).
- Give an overview over your infrastructure in a nice way:

    - Version of your Fortinet devices,
    - Version distribution of the FortiClients managed by your FortiClient EMS
    - Some summary information of your (backed up) FortiGate configurations


fotoobo vs. FortiXYZ REST API
-----------------------------

There is a general purpose API for all of the supported devices. Fotoobo uses them all to "talk" to
the respective device, so basically its no "vs.". For you this means you are always free to
implement your use cases in own scripts directly utilizing the REST API. What fotoobo can offer you
is to remove the boiler plate code needed to get and push data to the respective APIs. See the
`fotoobo Module Documentation <_ModuleDocumentation>`_ for further information on whether fotoobo
is usable to you. If not, please help us to make it so :-).

fotoobo vs. Fortinet ansible module
-----------------------------------

The main goal of fotoobo is not (yet) to provide tools to manipulate the configuration of the
respective devices. For this please use the
`Fortinet ansible module <https://docs.ansible.com/ansible/latest/collections/fortinet/index.html>`_
or the REST API's directly.

What fotoobo can do for you in this cases is for example information gathering and enhancing, e.g.
through the `convert` commands.
