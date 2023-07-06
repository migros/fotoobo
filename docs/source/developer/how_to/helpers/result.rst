.. Describes the helper class results

.. :orphan: is used so that Sphinx does not complain about not having this file in any toctree.

:orphan:

.. _how_to_helpers_result:

How To Use The Results Helper
=============================

Here we document some important Result methods.


print_result_as_table()
-----------------------

The print_result_as_table() method uses the results in a :code:`Results()` object to print a rich
formatted table. The value of the results may be any kind of type but there is some magic if the
type is a dict. See the following examples for clarification.

Results with int
^^^^^^^^^^^^^^^^

If you push results with an int as value you can print a pretty table with every result as a line.
The name of the result will be the first column and the value will be the second table.

..  code-block:: python

    from fotoobo.helpers import result
    res = result.Result()
    res.push_result("host1", 1)
    res.push_result("host2", 2)
    res.all_results()

..  code-block:: text

    {'host1': 1, 'host2': 2}

..  code-block:: python

    res.print_result_as_table()

..  code-block:: text

    ┌───────┬───┐
    │ host1 │ 1 │
    │ host1 │ 2 │
    └───────┴───┘

With the :code:`auto_header` argument set to :code:`True` you may also print headers. With simple
data types the headers for the both columns are always :code:`key` and :code:`value`. Of course you
could always rename these headers with the :code:`headers` argument. 

..  code-block:: python

    res.print_result_as_table(auto_header=True)

..  code-block:: text

    ┏━━━━━━━┳━━━━━━━┓
    ┃ key   ┃ value ┃
    ┡━━━━━━━╇━━━━━━━┩
    │ host1 │ 1     │
    │ host2 │ 2     │
    └───────┴───────┘

Other simple data types which behave the same are str, float or bool. All these types may be mixed
in a single Results() object.

Results with list
^^^^^^^^^^^^^^^^^

Lists in a results value are not interpreted as a complex data type and therefore just printed as
a pretty list. None of the lists or list items are interpreted as special or interesting data. Like
with other simple data types results with lists as values always print a table with two columns.
The same applies for tuples. 

..  code-block:: python

    from fotoobo.helpers import result
    res = result.Result()
    res.push_result("host1", ["a", "b", "d"])
    res.push_result("host2", ["x", "y", "z"])
    res.all_results()

..  code-block:: text

    {'host1': ['a', 'b', 'd'], 'host2': ['x', 'y', 'z']}

..  code-block:: python

    res.print_result_as_table()

..  code-block:: text

    ┌───────┬──────────┐
    │ host1 │ [        │
    │       │     "a", │
    │       │     "b", │
    │       │     "d"  │
    │       │ ]        │
    │ host2 │ [        │
    │       │     "x", │
    │       │     "y", │
    │       │     "z"  │
    │       │ ]        │
    └───────┴──────────┘

Like with other simple datatypes results with lists or tuples may be mixed arbitrary.

Results with dict
^^^^^^^^^^^^^^^^^

Here we bring some magic into the game. Whenever you push a dict to a result the table printed will
use the keys of the dict as columns. With this given it is very important that every dict in all
results have the same keys (names and sequence must match). As a best practice always use loop
generated dicts whenever you need them as results.

..  code-block:: python

    from fotoobo.helpers import result
    res = result.Result()
    res.push_result("host1", {
        "version": 1,
        "build": 2000,
        "host": "host1.local"
    })
    res.push_result("host2", {
        "version": 2,
        "build": 2020,
        "host": "host2.local"
    })
    res.all_results()

..  code-block:: text

    {'host1': {'version': 1, 'build': 2000, 'host': 'host1.local'}, 'host2': {'version': 2, 'build': 2020, 'host': 'host2.local'}}

..  code-block:: python

    res.print_result_as_table()

..  code-block:: text

    ┌───────┬───┬──────┬─────────────┐
    │ host1 │ 1 │ 2000 │ host1.local │
    │ host2 │ 2 │ 2020 │ host2.local │
    └───────┴───┴──────┴─────────────┘

You see that the keys of the dicts are not visible with standard output. Use the
:code:`auto_header` argument the show the dict keys as column headers.

..  code-block:: python

    res.print_result_as_table(auto_header=True)

..  code-block:: text

    ┏━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ key   ┃ version ┃ build ┃ host        ┃
    ┡━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━┩
    │ host1 │ 1       │ 2000  │ host1.local │
    │ host2 │ 2       │ 2020  │ host2.local │
    └───────┴─────────┴───────┴─────────────┘

Of course you may also use the :code:`headers` argument if you'd like to customize header names.

Results with dict when dicts are not consistent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the magic we use with dicts in results you'll get unwanted output if you mix types or change
the key names or order.

..  code-block:: python

    from fotoobo.helpers import result
    res = result.Result()
    res.push_result("host1", {
        "version": 1,
        "build": 2000,
        "host": "host1.local"
    })
    res.push_result("host2", {
        "host": "host2.local",
        "version": 2
    })
    res.push_result("host3", "text")
    res.all_results()

..  code-block:: text

    {'host1': {'version': 1, 'build': 2000, 'host': 'host1.local'}, 'host2': {'host': 'host2.local', 'version': 2}, 'host3': 'text'}

..  code-block:: python

    res.print_result_as_table(auto_header=True)

..  code-block:: text

    ┏━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ key   ┃ version     ┃ build ┃ host        ┃
    ┡━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━┩
    │ host1 │ 1           │ 2000  │ host1.local │
    │ host2 │ host2.local │ 2     │             │
    │ host3 │ text        │       │             │
    └───────┴─────────────┴───────┴─────────────┘

You would expect a table which looks like the line for host1. But for host2 you recognize that the
hostname is in the wrong column. This is because the order of the key value pairs in the dict does
not match the ordering of the first result. With host3 which not even has a dict as value you see
that the value given is just printed in the second column.

Conclusion: **Stay consequent with dicts in results!**


print_table_raw()
-----------------

The method :code:`print_table_raw()` takes the data to print as first argument. You always have to
pass a list of dicts or it will raise an exception. Every item in the list will result in a line in
the table and every key in the dict will represent a column. The table will only contain the values
in the dicts whereas the keys will be interpreted as colum headers. It is very important that every
dict in all results have the same keys (names and sequence must match). As a best practice always
use loop generated dicts whenever you need them in a table.

..  code-block:: python

    from fotoobo.helpers import result
    res = result.Result()
    data = [
        {
            "key": "host1",
            "version": 1,
            "build": 2000,
            "host": "host1.local"
        },
        {
            "key": "host2",
            "version": 2,
            "build": 2020,
            "host": "host2.local"
        }
    ]
    res.print_table_raw(data, auto_header=True)

..  code-block:: text

    ┏━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ key   ┃ version ┃ build ┃ host        ┃
    ┡━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━┩
    │ host1 │ 1       │ 2000  │ host1.local │
    │ host2 │ 2       │ 2020  │ host2.local │
    └───────┴─────────┴───────┴─────────────┘


