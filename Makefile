
fuzzer_cov_python ?= python3

build:
	$(fuzzer_cov_python) setup.py sdist bdist_wheel

upload: build
	$(fuzzer_cov_python) -m twine upload --skip-existing -r pypi dist/*

main:
	PYTHONPATH="$(PWD):${PYTHONPATH}" $(fuzzer_cov_python) -m fuzzer_cov

.PHONY: build upload main
