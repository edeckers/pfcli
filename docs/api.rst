Commands
========

Firmware
-------

*Output version information*

Optional arguments:

`--format`: output format either `json` or `text`, defaults to `text`

.. code-block:: bash

    pfcli firmware version

Info
-------

*Output general configuration information*

Optional arguments:

`--format`: output format either `json` or `text`, defaults to `text`

.. code-block:: bash

    pfcli info

Unbound
-------

Host overrides
~~~~~~~~~~~~~~

*List host overrides*

Optional arguments:

`--format`: output format either `json` or `text`, defaults to `text`
`--sorted`: sort the output by domain, defaults to `false`

.. code-block:: bash

    pfcli unbound list-host-overrides

*Add host override*

Optional arguments:

`--description`: description of the host override
`--reason`: reason for the host override, stored in update logs

.. code-block:: bash

    pfcli unbound add-host-override --domain <your-domain> --host <your-host> --ip <your-ip>

*Delete host override*

*WARNING* use the _unsorted_ index of the host overrides: unfortunately the PfSense implementation uses indices instead of unique identifiers, which is extremely fragile and might cause race conditions.

Optional arguments:

`--reason`: reason for deleting host override, stored in update logs

.. code-block:: bash

    pfcli unbound delete-host-override --index <index>