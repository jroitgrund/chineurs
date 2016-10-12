default: pylint pytest

pytest:
	pytest

pylint:
	pylint $(shell find chineurs tests -name "*.py")
