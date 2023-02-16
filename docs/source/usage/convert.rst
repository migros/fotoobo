.. Describes the object converter

.. _convert:

Configuration Object Converter
==============================

This module can be used to convert configuration objects from other vendors into Fortinet syntax.
Each vendor is represented as a subcommand. The following vendors are supported:

* Checkpoint


Checkpoint Object Converter
---------------------------

.. code-block:: bash

    fotoobo convert checkpoint [infile] [outfile] [obj_type] [cache_dir]

infile
    specifies the json file containing the Checkpoint objects. The [obj_type] has to be the top
    level dict in the json file containing data for the specified type. The json file has to be in
    the following format:

    .. code-block:: json

        {
            "hosts": [
                {
                    "...": "..."
                }
            ],
            "networks": [
                {
                    "...": "..."
                }
            ],
            "groups": [
                {
                    "...": "..."
                }
            ]
        }

outfile
    specifies the json file to write the Fortinet specific objects into.

type
    specifies the type of objects to convert. If [type] is omitted, the converter tries to convert all objects in the [infile]. The following types are supported. Click on the link to see it's field mapping.

    * hosts
    * networks
    * address_ranges
    * groups
    * services_icmp
    * services_icmp6
    * services_tcp
    * services_udp
    * service_groups

cache_dir
    Specifies the cache directory to use. If given, the converted outfile will be cached into this
    directory. Subsequent convert jobs will only return new assets which are not already in this
    cache.

    Be aware that caching only affects the convert function. If further steps in your process do
    result in an error the cache is not affected (thus left updated).

The following mappings take place when converting checkpoint objects into Fortinet objects:

.. image:: convert_checkpoint_mappings.drawio.svg
  :width: 100%
  :alt: The fotoobo convert checkpoint mapings




