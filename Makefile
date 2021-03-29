
fuzzer_cov_python ?= python3

gen_readme:
	$(fuzzer_cov_python) scripts/gen_readme.py

build: gen_readme
	$(fuzzer_cov_python) setup.py sdist bdist_wheel

upload: build
	$(fuzzer_cov_python) -m twine upload --skip-existing -r pypi dist/*

main:
	$(fuzzer_cov_python) -m fuzzer_cov

.PHONY: build upload main
