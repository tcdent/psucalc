
import sys, argparse
from psucalc import *
from psucalc import doc

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("config", nargs='?', default=None)
    args = parse.parse_args()

    print(MOTD.format(**ANSI))

    if args.config:
        config = eval(open(args.config).read(), globals())
        config()
    else: # help
        print(doc.__doc__)

# if __name__ == "__main__":
#     main()