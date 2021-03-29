
import argparse

from fuzzer_cov import version

def parse_cmdline():

    # opts.output_dir = os.path.realpath('.material/fuzz-cov')

    p = argparse.ArgumentParser()
    p.prog = "fuzzer_cov"

    p.add_argument("--version", action='store_true',
        help="print version string", default=False)

    return p, p.parse_args()

def main():
    p, args = parse_cmdline()

    if args.version:
        print(version)
    else:
        p.print_help()

if __name__ == '__main__':
    main()