all: bootstrap develop test

bootstrap:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

develop:
	python setup.py develop

test: clean develop lint
	py.test

lint:
	flake8 --ignore=E501,E702 .

clean: clean-build
	find . -name '*.py[co]' -exec rm -f {} +

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

release: clean clean-build test docs
	prerelease && release
	git push --tags
	git push

doc: clean develop
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

open_doc: doc
	open docs/_build/html/index.html
