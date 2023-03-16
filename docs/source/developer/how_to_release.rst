.. Describes how to do a new release

.. _HowToRelease:

How to Release
==============

Only maintainers are allowed to release code. So, if someone did some breaking changes which should
be released ask a maintainer to do so.

Making a release is done by a strictly defined process. To help you publishing a release there are
some scripts and workflows which do some checks and automation.

Here are the steps you need to perform to make a release.

#. Make sure all tests pass
#. Update the changelog
#. Execute the ``.make_release.sh`` script giving the type of release (major/minor/patch)
#. Make a pull request
#. Switch to the main repository (migros/fotoobo)
#. Execute the ``.tag_release.sh`` script

.make_release.sh
----------------

The script `.make_release.sh <https://github.com/migros/fotoobo/blob/main/.make_release.sh>`_ 
prepares the repository for the release, does some simple checks and releases the code and its
documentation. These are the steps it goes through:

#. It checks if there are uncommitted changes in the repository
#. It bumps the version by using ``poetry version``
#. It asks you if the new version is correct
#. It writes the new version to `fotoobo/__init__.py` 
#. It commits the changes to the repository
#. It pushes the repository to the remote

.tag_release.sh
---------------

The script `.tag_release.sh <https://github.com/migros/fotoobo/blob/main/.tag_release.sh>`_ just
creates the release tag. This script has to be run the main repository `migros/fotoobo
<https://github.com/migros/fotoobo>`_.

#. It creates a git tag with the version
#. It pushes the tag to the repository

The release workflow
--------------------

Whenever a tag is pushed the release workflows are started.

* The `create-github-release.yaml 
  <https://github.com/migros/fotoobo/blob/main/.github/workflows/create-github-release.yaml>`_ 
  workflow is creates the release on GitHub.
* The `publish-to-pypi.yaml
  <https://github.com/migros/fotoobo/blob/main/.github/workflows/publish-to-pypi.yaml>`_ workflow
  publishes the package to the PyPI registry.
