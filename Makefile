test:
	mkdir -p $(shell echo $CIRCLE_TEST_REPORTS)/pytest
	pytest --junitxml=pytest/pytest.xml

lint:
	pylint $(shell find chineurs tests -name "*.py")
