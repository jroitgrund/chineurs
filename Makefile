test:
	mkdir -p $(shell echo $CIRCLE_TEST_REPORTS)/junit
	pytest --junitxml=junit/junit.xml

lint:
	pylint $(shell find chineurs tests -name "*.py")
