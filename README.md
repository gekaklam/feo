## About

Feo, as a reference to iron oxide (here Fe2O3) which is commonly used in magnetic tape media, allows to simulate automated tape libraries systems integrated into the storage hierarchy of modern data centers.

## Dependencies

http://graph-tool.skewed.de/

# Compiling graph-tool from source

	sudo dnf install CGAL CGAL-devel cairomm cairomm-devel pycairo pycairo-devel sparsehash-devel boost boost-python3 boost-python3-devel
	sudo pip3 install numpy scipy

Build and install using the following instructions:

	export PYTHON=/usr/bin/python3
	./configure --with-boost-python=boost_python3 --disable-cairo
