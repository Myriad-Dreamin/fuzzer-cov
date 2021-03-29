
fuzzer_cov_python ?= python3

gen_readme:
	$(fuzzer_cov_python) scripts/gen_readme.py

build: gen_readme
	$(fuzzer_cov_python) setup.py sdist bdist_wheel

upload: build
	$(fuzzer_cov_python) -m twine upload --skip-existing -r pypi dist/*

main:
	$(fuzzer_cov_python) -m fuzzer_cov

protobuf_fuzz_dir ?= ../../sda2/protobuf-fuzz
protobuf_fuzz_cov_options ?= 
protobuf_fuzz_cov_options += --fuzzer $(protobuf_fuzz_dir)/cmake-build-relwithdebinfo/src/kfuzz_mali_gcov
protobuf_fuzz_cov_options += -s $(protobuf_fuzz_dir)/
protobuf_fuzz_cov_options += -o $(protobuf_fuzz_dir)/.material/fuzz-cov
protobuf_fuzz_cov_options += -c $(protobuf_fuzz_dir)/fuzz-corpus3/a
protobuf_fuzz_cov_options += --lcov-exclude-pattern "$(protobuf_fuzz_dir)/src/userspace/\*"

protobuf-fuzz-example:
	$(fuzzer_cov_python) -m fuzzer_cov.commands.libfuzzer $(protobuf_fuzz_cov_options) 

.PHONY: build upload main
