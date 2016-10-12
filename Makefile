test:
	pytest --junitxml=junit.xml

lint:
	pylint $(shell find chineurs tests -name "*.py")
