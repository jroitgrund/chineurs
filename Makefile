default: lint test

test:
	mkdir -p $(CIRCLE_TEST_REPORTS)/junit
	pytest --junitxml=$(CIRCLE_TEST_REPORTS)/junit/junit.xml --cov=chineurs --cov-report term-missing

lint:
	pylint $(shell find chineurs tests -name "*.py") --disable=locally-disabled
