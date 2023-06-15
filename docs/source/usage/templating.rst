.. Here we document the results templating

.. _usage_templating:


Templating the Output
=====================

Some of the tools allow you to customize the output with templates. This gives you the ability to
customize the output to your needs. We use the `Jinja2 <https://palletsprojects.com/p/jinja/>`_
templating engine.

Any command which has the ability to use a Jinja2 template has the respective options. You can see
then when calling the help:

..  code-block:: bash

    $ fotoobo ems monitor connections -h

    # some output is omitted here

    ╭─ Options ───────────────────────────────────────────────────────────────────────────────╮
    │ --output    -o   [output]    The file to write the output to. [default: None]           │
    │ --raw       -r               Output raw data.                                           │
    │ --template  -t   [template]  The jinja2 template to use (use with -o). [default: None]  │
    │ --help      -h               Show this message and exit.                                │
    ╰─────────────────────────────────────────────────────────────────────────────────────────╯


The --raw Option
----------------

To get an idea of what values you may use in a Jinja2 template use the option ``--raw``. This
gives you the raw json representation of the generated data.

**Example for raw output**

..  code-block:: bash

    $ fotoobo ems monitor connections --raw
    {
    │   'data': [
    │   │   {
    │   │   │   'token': 'offlineLong',
    │   │   │   'value': 111,
    │   │   │   'name': 'Offline for 30 days or more'
    │   │   },
    │   │   {
    │   │   │   'token': 'offlineNominal',
    │   │   │   'value': 222,
    │   │   │   'name': 'Offline'
    │   │   },
    │   │   {
    │   │   │   'token': 'offlineRecent',
    │   │   │   'value': 333,
    │   │   │   'name': 'Offline for less than 1 hour'
    │   │   },
    │   │   {
    │   │   │   'token': 'online',
    │   │   │   'value': 444,
    │   │   │   'name': 'Online'
    │   │   }
    │   ],
    │   'fotoobo': {
    │   │   'offlineLong': 111,
    │   │   'offlineNominal': 222,
    │   │   'offlineRecent': 333,
    │   │   'online': 444
    │   }
    }


Accessing the Data
------------------

Normally we see two keys in the main dictionary (**data** and **fotoobo**) where **data** contains
the raw data returned from the accessed device and **fotoobo** is calculated data from within the
used tool (which in this case was ``ems monitor connections``)

Let's assume you want to access the **online** value in the **fotoobo** context. Simply use the
following syntax in your template:

..  code-block:: text

    {{ fotoobo.online }}


Templating Example
------------------

Assuming we still use the same raw output as above we can use the following template to write our
output to a file

..  code-block:: text
    :caption: template.j2

    There are {{ fotoobo.online }} clients online.

Now run the tool with the template and the desired output file:

..  code-block:: bash

    $ fotoobo ems monitor connections -t template.j2 -o output.txt

Finally you'll find your output file with the following content:

..  code-block:: text
    :caption: output.txt
    
    There are 444 clients online.
    
Of course this is just a minimalistic example of what templates can do for you. If you need more
sophisticated output please see the documentation and examples on the
`Jinja2 <https://palletsprojects.com/p/jinja/>`_ Homepage.

`Have fun with templates!`
