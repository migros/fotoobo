.. Describes how to do write tests

.. _how_to_test:

How To Test
===========

To test the code we use `pytest <https://docs.pytest.org/>`_.

Tests Structure
---------------

According to `Anatomy of a test <https://docs.pytest.org/en/stable/explanation/anatomy.html>`_ we use the Arrange, Act, Assert, (Cleanup) terminology for every test function or method.

**Good Example**

..  code-block:: python

    from pathlib import Path

    def test_good() -> None:
        """
        Test something with good style.
        """

        # Arrange
        test_file = Path("testfile.txt")
        test_file.write_text("Hello")
        assert test_file.exists()

        # Act
        my_test_function(testfile)

        # Assert
        text = testfile.read_text()
        assert "Hello" in text

**Bad Example**

..  code-block:: python

    from pathlib import Path

    def test_bad() -> None:
        """
        Test something with bad style.
        """
        test_file = Path("testfile.txt")
        test_file.write_text("Hello")
        assert test_file.exists()
        my_test_function(testfile)
        text = testfile.read_text()
        assert "Hello" in text

Static Data
-----------

If you need static data for your tests use the directory *tests/data*. There you can put your data.
If you change existing data make sure you do not break other tests. Make sure to not add any kind of
productive and sensitive data into this directory as it is pushed to the repository.

Temporary Data
--------------

For temporary data use the pytest `TempPathFactory 
<https://docs.pytest.org/en/8.0.x/reference/reference.html#pytest.TempPathFactory>`_. See the
following example on how to setup a temporary directory.

..  code-block:: python

    from pathlib import Path

    import pytest

    @pytest.fixture(scope="session")
    def session_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
        """
        Creates and maintains a session temp directory.
        """
        
        return tmp_path_factory.mktemp("session_")

There is also the same for module or function scope depending on how long you wish your temp directory exists. These fixtures are predefined in *tests/conftest.py* so you can use it in any test function or method.

Mocking
-------

For mocking we use the pytest predefined `monkeypatch
<https://docs.pytest.org/en/7.1.x/reference/reference.html#monkeypatch>`_ fixture.

**Good Example**

..  code-block:: python

    from unittest.mock import Mock
    
    import pytest

    def test_something_correct(monkeypatch: pytest.MonkeyPatch):
        """
        This tests something the preferred way.
        """
        
        monkeypatch.setattr("path.to.your.object", Mock(return_value=None))
        ...

**Bad Example**

..  code-block:: python

    from unittest.mock import Mock, patch

    @patch("path.to.your.object", Mock(return_value=None))
    def test_something_wrong():
        """
        This tests something the wrong way.
        """
        
        ...
