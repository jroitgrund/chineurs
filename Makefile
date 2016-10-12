pytest:
	pytest --junitxml=junit.xml

pylint:
	pylint $(shell find chineurs tests -name "*.py")
