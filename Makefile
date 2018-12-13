PYPI_SERVER = https://test.pypi.org/legacy/

.PHONY: clean-pyc
clean-pyc: ## Remove Python file artifacts
	@echo "+ $@"
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

.PHONY: clean-build
clean-build: ## Remove build artifacts
	@echo "+ $@"
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

.PHONY: clean
clean: clean-build clean-pyc

.PHONY: test
test: ## Run tests quickly with the default Python
	@echo "+ $@"
	@python2 -m turksuffixer/tests/test

.PHONY: check
check: 
	@python2.7 -m flake8 --max-line-length=88 --exclude turksuffixer/tests,example*.py

.PHONY: build
build: sdist

.PHONY: sdist
sdist: clean ## Build sdist distribution
	@echo "+ $@"
	@python setup.py sdist
	@ls -l dist

.PHONY: upload
upload:
	@echo "+ $@"
	@twine upload -u talha252 --repository-url $(PYPI_SERVER) dist/*

.PHONY: release
release: build upload clean
