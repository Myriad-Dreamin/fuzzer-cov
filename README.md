
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
## output of command help ##
```

## CLI Usage

print help

```shell
$ python3 -m fuzzer_cov --help
usage: __main__.py [-h] --fuzzer FUZZER -s SRC -o OUT -c CORPUS_DIR
                   [--lcov-follow-links] [--enable-branch-coverage]
                   [--lcov-exclude-pattern LCOV_EXCLUDE_PATTERN]
                   [--lcov-path LCOV_PATH] [--gen-html-path GEN_HTML_PATH]
                   [-v] [-V] [-q]

optional arguments:
  -h, --help            show this help message and exit
  --fuzzer FUZZER       Fuzzer Path (gcov instrumented)
  -s SRC, --src SRC     Source root directory
  -o OUT, --out OUT     Coverage output directory
  -c CORPUS_DIR, --corpus-dir CORPUS_DIR
                        Corpus (inputs) Directory
  --lcov-follow-links   Follow links when searching .da files
  --enable-branch-coverage
                        Include branch coverage in code coverage reports (may
                        be slow)
  --lcov-exclude-pattern LCOV_EXCLUDE_PATTERN
                        Set exclude pattern for lcov results
  --lcov-path LCOV_PATH
                        Path to lcov command
  --gen-html-path GEN_HTML_PATH
                        Path to genhtml command
  -v, --verbose         Verbose mode
  -V, --version         Print version and exit
  -q, --quiet           Quiet mode

```
