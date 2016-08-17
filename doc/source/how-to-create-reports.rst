.. TapeSim documentation master file, created by
   sphinx-quickstart on Tue Oct 27 21:17:57 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started: Creating Reports
=================================

FEO was developed to provide insight into hierarchical storage systems and
especially to conduct research on how to improve the performance and Quality of
Service (QoS) of such systems.  Feo comes with a number of different tools and
scripts to gather the necessary data during simulation as well as extracting
and visualising the results.

.. contents::

Overview
--------

* Request data
	* requests.csv for request summaries (e.g. throughput, duration, size, status/errors)
	* stages.csv 
	* wait-times.csv 
	* Detailed request histories including bandwidth changes (optional)
* Simulation process log when enabled (Default: stdout)
* Simulation state in limited detail (dumped at the end of the simulation)
	* Filesystem state
	* Tape system state (Tapes and Slots)
	* Global cache state
* HSM/Tape System Configuration
	* Network Topology as XML
	* Library Topology (pickle/XML)



API
---

.. autoclass:: tapesim.
    :members:
    :inherited-members:
