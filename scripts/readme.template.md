
# fuzzer-cov

fuzzer coverage tool, generate readable coverage report in html format

## Prerequisite

### Install lcov package
on ubuntu:

```shell
apt-get install lcov
```

## Installation

```shell
$ python3 -m pip install fuzzer-cov
```

Verify that the pacakge is installed successfully.

```shell
$ python3 -m fuzzer_cov --help
{{insert_point:`python3 -m fuzzer_cov --help`}}
```

## CLI Usage

### LibFuzzer

generate coverage report for [LibFuzzer](https://llvm.org/docs/LibFuzzer.html).

```shell
$ python3 -m fuzzer_cov.commands.libfuzzer --help
{{insert_point:`python3 -m fuzzer_cov.commands.libfuzzer --help`}}
```
