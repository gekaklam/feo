## About

Feo, as a reference to iron oxide (here Fe2O3) which is commonly used in magnetic tape media, allows to simulate automated tape libraries systems integrated into the storage hierarchy of modern data centers.

## Requirements

Feo is written in Python 3 and requires graph-tool[1] (a python wrapper for C++ 
graph functions).

[1] http://graph-tool.skewed.de/

### Compiling graph-tool from source

Unfortunetly graph-tool can not be installed using pip but needs to be compiled
from source. For Fedora all requirements for graph-tool can be satisfied by
by installing the following:

	sudo dnf install CGAL CGAL-devel cairomm cairomm-devel pycairo pycairo-devel sparsehash-devel boost boost-python3 boost-python3-devel
	sudo pip3 install numpy scipy

Build and install using the following instructions:

	export PYTHON=/usr/bin/python3
	./configure --with-boost-python=boost_python3 --disable-cairo
