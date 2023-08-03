.. Chapter eight according to https://arc42.org/overview

.. _CrosscuttingConcepts:


7. Crosscutting concepts
========================

Separation of Input, Output and Processing
------------------------------------------

For **fotoobo** to be easily extendable with additional interfaces the input/output and processing
layer need to be strictly separated. This is done by several measures:

- Passing of **input** parameters is done by using parameters only. Any input specific parameter
  preprocessing should be done on the input/output layer.
- Passing of **return** values is done by using a common `Result` class (see below).
- The **processing** of the request is done by a so called **fotoobo** "tool", inside the **tools**
  directory.


Common Result class
-------------------

For passing output of a **fotoobo** tool to the interface there is a common `Result` class found
in the fotoobo helpers.

See :ref:`how_to_helpers_result` for more information about this.


Parallelization
---------------

By separating the *processing* from the *intput/output* part running a task in parallel against
several Fortinet devices becomes easier to do. Please follow some guidelines when doing this:

- *Always* do the parallelization inside a tool. The *input/output* layer should not be concerned
  about parallelization at all (except for example disabling it on request, if applicable).
- You *should* make a nested function inside the tool function that will query one Fortinet instance
  and return the raw data.
- Then use `ThreadPoolExecutor <https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor>`_
  of the Python `concurrent.futures` standard library to process and execute the single parts as
  depicted below.


.. code-block:: python

    def my_tools_method(any, parameters, needed) -> Result:
        """
        Example for parallelization, taken from tools.fgt.get.version()

        This example also includes the display of a progress bar on the console using
        rich.progress.Progress().
        """
        def _get_single_version(name: str, fgt: FortiGate):
            """
            Get version for single FortiGate.

            NOTE: Method shortened for legibility
            """
            fortigate_version = fgt.get_version()

            return name, fortigate_version

        result = Result[str]()

        with Progress() as progress:
            task = progress.add_task("getting FortiGate versions...", total=len(fgts))
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                # Register all the tasks that need to be done
                for name, fgt in fgts.items():
                    futures.append(executor.submit(_get_single_version, name, fgt))

                # Process the results of the single tasks as they are finished
                for future in concurrent.futures.as_completed(futures):
                    name, fortigate_version = future.result()
                    result.push_result(name, fortigate_version)
                    progress.update(task, advance=1)

        return result
