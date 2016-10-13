default: lint test

test:
	mkdir -p $(CIRCLE_TEST_REPORTS)/junit
	pytest --junitxml=$(CIRCLE_TEST_REPORTS)/junit/junit.xml

lint:
	flake8 $(shell find chineurs tests -name "*.py")
