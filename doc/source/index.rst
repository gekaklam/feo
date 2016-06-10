.. TapeSim documentation master file, created by
   sphinx-quickstart on Tue Oct 27 21:17:57 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Feo: Tape Library Simulator
==========================

Feo, as a reference to iron oxide (here Fe2O3) which is commonly used in magnetic tape media, allows to simulate automated tape libraries systems integrated into the storage hierarchy of modern data centers.

The system is modularized to relfect the various physical and software based components found in actual storage systems for two reasons: 1) to accurately resemble the paths data flows in actual systems 2) to allow to operate and manage actual enterprise tape systems once in a matured state.


.. toctree::
    :glob:
    :titlesonly:
    :maxdepth: 2



Table of Contents
----------

- :doc:`how-to-simulate`
- :doc:`how-to-create-reports`

- :doc:`components`






.. automodule:: tapesim

.. autoclass:: tapesim.Simulation.Simulation
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

