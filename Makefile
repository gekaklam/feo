init:
	    pip install -r requirements.txt

test:
	    nosetests

.PHONY: init test




dist:
	python3 setup.py sdist

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
