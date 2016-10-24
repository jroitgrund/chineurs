default: lint test

test:
	mkdir -p $(CIRCLE_TEST_REPORTS)/junit
	pytest --junitxml=$(CIRCLE_TEST_REPORTS)/junit/junit.xml --cov=chineurs --cov-report term-missing

lint:
	pylint --ignored-modules=chineurs.frontend $(shell find chineurs tests -path chineurs/frontend -prune -o -name "*.py") --disable=locally-disabled --disable=locally-enabled
	cd chineurs/frontend;npm run lint:js
