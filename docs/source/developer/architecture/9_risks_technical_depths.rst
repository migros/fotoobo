.. Chapter eleven according to https://arc42.org/overview

.. _RisksTechnicalDepths:

9. Risks & Technical Depths
============================

Use of undocumented API parts
-----------------------------

Description
^^^^^^^^^^^

To achieve some of its goals **fotoobo** makes use of undocumented API calls. This is due to
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


Use of unencrypted inventory including credentials
--------------------------------------------------

Description
^^^^^^^^^^^

Currently **fotoobo** may use only its own inventory format which is entirely unencrypted. The
required login data (tokens, username & password) need to be part of the inventory.

Risk
^^^^

Because of the supported functionality of **fotoobo** these credentials usually have admin rights on
the respective Fortinet devices. So loss of this information may pose a big security threat to the
company using **fotoobo**.

Mitigation
^^^^^^^^^^

There are several things done to mitigate this risk:

- **fotoobo** by default uses only encrypted and verified connections to communicate with the
  Fortinet devices and other backend systems. Lowering the security bar is in the user's hands and
  not the first suggestion in the documentation.
- The risk of exposing the inventory and how to minimize this risk is clearly stated in the
  documentation at :ref:`usage_inventory`.
- To make the handling of sensitive data a bit safer you may store such data in a Hashicorp Vault
  service which is documented here: :ref:`vault_service`.
