.. Chapter eleven according to https://arc42.org/overview

.. _RisksTechnicalDepths:

11. Risks & Technical Depths
============================

11.1 Use of undocumented API parts
----------------------------------

Description
^^^^^^^^^^^

To achieve some of its goals, **fotoobo** makes use of undocumented API calls. This is due to
missing functionality in the official Fortinet APIs.

Risk
^^^^

Undocumented API parts are subject to be changed at any time by Fortinet without notification or any
deprecation process. This will possibly break the respective **fotoobo** functionality.

Mitigation
^^^^^^^^^^

Any part of **fotoobo** is tested regularly against real Fortinet devices so we will get to know,
when some API calls break and break the respective **fotoobo** part.

*Note: This is done using a best-effort approach of the maintainers and is mostly based on the
regular use of the current* **fotoobo** *features using cron-jobs and alike.*


11.2 Use of unencrypted inventory including security tokens
-----------------------------------------------------------

Description
^^^^^^^^^^^



Risk
^^^^


Mitigation
^^^^^^^^^^

TODO
