
all:
	@echo Please specify a target.
	@echo "Example: make test"


deps:
	pip3 install -r requirements.txt

dist:
	python3 setup.py sdist

test:
	py.test tests

install:
	python3 setup.py install



clean:
	rm -rf build

	rm -rf dist
	rm -rf feo_tape_library_simulation.egg-info


clean-pyc:
	# use to remove any *.pyc files which may be created during development
	@echo TODO
	find tapesim -name "*.pyc" | xargs rm
