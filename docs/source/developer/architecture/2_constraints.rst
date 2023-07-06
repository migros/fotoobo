.. Chapter one according to https://arc42.org/overview

.. _2Constraints:

2. Constraints
==============

The Fortinet-APIs
-----------------

Not all functionality that **fotoobo** offers or likes to offer is possible with the use of the
*documented* API of the respective Fortinet product. Sometimes there is a possibility to use
undocumented API calls learned by debugging the official web interface of the respective product.
But these cases are risky because Fortinet does not necessarily keep backwards compatibility for
these API calls and will also not document any changes.
Other times we can not overcome the limitations and need to use other ways to get the required
information - historically we used SNMP for such a case which is now using the REST API again.

This is another reason **fotoobo** does mostly just read, but not write to the APIs to prevent
unintended side effects by using undocumented API parts.
