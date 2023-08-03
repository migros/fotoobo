.. Chapter ten according to https://arc42.org/overview

.. _QualityAssurance:

10. Quality Assurance
=====================

Since most Fortinet products are security devices the stability and reliability of those devices is
crucial to companies using **fotoobo**. **fotoobo** thus needs to be well tested, stable and reliable
too.

Quality Goals
-------------

In particular **fotoobo** should be:

- **Reliable**:

  - Updates and changes to **fotoobo** should not break any existing functionality, if not
    otherwise noted (and allowed by `Semantic Versioning <https://semver.org/>`_).
  - **fotoobo** should behave the same on every request and as such should only depend on the input
    data given for the current request (and some weird internal state).

- **Usable**:

  - The use of **fotoobo** should be as intuitive as possible for the core audience (computer
    network & security professionals).
  - The use of **fotoobo** should be well documented using an example based approach.

- **Secure**:

  - **fotoobo** tries to use secure transmission by default everywhere and will not store or cache
    any sensitive information anywhere it was not instructed to.


How quality assurance is done
-----------------------------

Testing, Types & Linting
^^^^^^^^^^^^^^^^^^^^^^^^

A high code quality is the foundation of a stable and reliable software. We especially do the
following:

- The use of *static typing* using MyPy minimizes the risk of runtime errors based on using wrong
  types.
- The use of *linting* using Pylint and enforcing consistent *code formatting* using Black and isort
  ensures that the code uses consistent formatting.
- The use of *unit-* and *integration tests* with a minimum coverage of at least 90% ensures a high
  degree of resilience against accidental errors and regressions.

  - *Unit testing* ensures that the basic functionality of every layer is consistently working.
  - *Integration testing* ensures that the user experience remains consistent by testing the
    whole stack by running the respective commands and parsing the output for the expected answers
    and formatting.

All of these are part of a build pipeline at Github that any pull request must pass before being
able to be merged into the `main` branch. This is enforced by the repository settings.


Four eyes principle
^^^^^^^^^^^^^^^^^^^

Any pull request must be reviewed by a maintainer (other than the one that opened the pull request,
if this person happens to be **fotoobo** maintainer) before it can be merged into the `main` branch.
This provides another layer of security to accidental or evil code changes. This principle is
enforced by the repository settings.


Extensive Documentation
^^^^^^^^^^^^^^^^^^^^^^^

Part of the **usability** goal is to not only have a simple to use user interface but also a well
understandable documentation.

Every new user is encouraged to give us feedback where possible problems were and how we could
improve the documentation to avoid these for future users. If the maintainers know the users
personally this encouragement is often expressed explicitly when talking about **fotoobo**.

Furthermore documentation should be *example based* and describe how to use **fotoobo**. Reference
documentation is important and also provided but should not be the first contact for **fotoobo**
users.