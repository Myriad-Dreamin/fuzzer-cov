
fuzzer_cov_python ?= python3

build:
	$(fuzzer_cov_python) setup.py sdist bdist_wheel

upload: build
	$(fuzzer_cov_python) -m twine upload --skip-existing -r pypi dist/*


.PHONY: build upload