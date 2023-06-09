.. Describes how to do write tests

.. _HowToTest:

How to Test
===========

To test the code we use pytest `pytest <https://docs.pytest.org/>`_.

Static Data
-----------

If you need static data for your tests use the directory *tests/data*. There you can put your data.
If you change existing data make sure you do not break other tests. Make sure to not add any kind of
productive and sensitive data into this directory as it is pushed to the repository.

Temporary Data
--------------

For temporary data use the temp fixture of pytest. See the following example on how to setup a 
temp dir.

..  code-block:: python

    @pytest.fixture(scope="session")
    def temp_dir(tmp_path_factory):  # type: ignore # (it's a pathlib.Path object)
        """creates and maintains a session temp directory"""
        return tmp_path_factory.mktemp("tests_")

This fixture is predefined in *tests/contest.py* so you can use it in any test.


Mocking
-------

For mocking we use the pytest `monkeypatch
<https://docs.pytest.org/en/7.1.x/reference/reference.html#monkeypatch>`_ method.

**Do not use:**

..  code-block:: python

    from unittest.mock import MagicMock, patch

    @patch("path.to.your.object", MagicMock(return_value=None))
    def test_something_wrong()
        """This tests something the wrong way"""
        pass

**But instead use:**

..  code-block:: python

    from _pytest.monkeypatch import MonkeyPatch

    def test_something_correct(monkeypatch: MonkeyPatch)
        """This tests something the right way"""
        monkeypatch.setattr("path.to.your.object", MagicMock(return_value=None))
        pass

