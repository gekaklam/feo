## About

Feo, as a reference to iron oxide (here Fe2O3) which is commonly used in magnetic tape media, allows to simulate automated tape libraries systems integrated into the storage hierarchy of modern data centers.


## Getting started

Assuming all requirements are met the easiest way to get started is by adapting
one of the prepared configurations in the example directory. 

    cd examples
    # use -h flag to show possible parameters and options for configurations
    ./RunTraceCRQ.py -h

    # or run with a default dummy configuration
    ./RunTraceCRQ.py


## Requirements

Feo is written in Python 3 and requires graph-tool (a python wrapper for C++ 
graph functions).

[1] http://graph-tool.skewed.de/

### Compiling graph-tool from source

Unfortunetly graph-tool can not be installed using pip but needs to be compiled
from source. E.g. on Fedora all requirements for graph-tool can be installed
as follows:

	sudo dnf install CGAL CGAL-devel cairomm cairomm-devel pycairo pycairo-devel sparsehash-devel boost boost-python3 boost-python3-devel
	sudo pip3 install numpy scipy matplotlib

Build and install using the following instructions:

	export PYTHON=/usr/bin/python3
	./configure --with-boost-python=boost_python3
	make
	sudo make install




