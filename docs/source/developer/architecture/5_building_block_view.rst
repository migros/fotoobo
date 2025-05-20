.. Chapter five according to https://arc42.org/overview

.. _BuildingBlockView:



5. Building Block View
======================

The layers of fotoobo
---------------------

There are three designated layers in **fotoobo**. These are the interface layer, the business logic
layer and the infrastructure layer.

.. image:: diagrams/fotoobo_layers.drawio.svg
  :width: 100%
  :alt: The layers of fotoobo visualized

In this diagram you see the designated paths to use when accessing a Fortinet device. Although these 
are the recommended ways to use it, you may also access the layers in other ways. Just keep in mind 
there always should be a rational and understandable approach.


The Interface Layer
^^^^^^^^^^^^^^^^^^^

This is the main entry point for interaction with **fotoobo** when you installed it as an
application on your system. It acts as a frontend for users and automation tools. At the Moment only
the CLI part is implemented. In future version a REST API may be available if there is a need for
it.

Call **fotoobo** with its command(s) directly from the command line or from any automation engine
like cron jobs, Rundeck or others.

The Business Logic Layer
^^^^^^^^^^^^^^^^^^^^^^^^

At this level you have access to specific use cases. These are called **tools** in **fotoobo**. Any
CLI command or API endpoint should point to such a **tool** which then interacts with the
infrastructure layer.

Whenever you use **fotoobo** as a module in your own code (instead of using it as an installed
application) you may directly access this layer.

The Infrastructure Layer
^^^^^^^^^^^^^^^^^^^^^^^^

In this lowest level of **fotoobo** we directly interact with the infrastructure, meaning we handle 
the authentication and API calls to the devices and services like FortiGate, FortiManger and 
others. The interface layer should not directly access this infrastructure layer. Instead there 
should always be a **tool** in the business logic layer which connects these two. No other layer 
than the infrastructure layer should directly access any fortinet device.

As a module in your own code you may also directly use the infrastructure layer.


Package structure
-----------------

The package structure describes the internal structure of **fotoobo**. The following diagram
visualizes the top level modules in the code. There are direct associations for these modules to 
the layers of **fotoobo**:

* cli: Interface Layer
* tools: Business Logic Layer
* fortinet: Infrastructure Layer


.. image:: diagrams/package_structure.drawio.svg
  :width: 100%
  :alt: The fotoobo package structure visualized


.. _fortinet_classes:

Class view
----------

.. image:: diagrams/classes.drawio.svg
  :width: 100%
  :alt: The fotoobo Fortinet classes visualized

