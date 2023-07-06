.. Chapter eight according to https://arc42.org/overview

.. _CrosscuttingConcepts:


8. Crosscutting concepts
========================

Separation of Input, Output and Processing
------------------------------------------

For **fotoobo** to be easily extendable with additional interfaces the input/output and processing
layer need to be strictly separated. This is done by several measures:

- Passing of **input** parameters is done only bu using parameters. Any input specific parameter
  preprocessing should be done on the input/output layer.
- Passing of **return** values is done by using a common `Result` class (see below).
- The **processing** of the request is done by a so called **fotoobo** tool, inside the **tools**
  directory.


Common Result class
-------------------

For passing output of a **fotoobo** tool to the interface there is a common `Result` class found
in the fotoobo helpers.


Parallelization
---------------

tbd

