import sys


def exit_code_zero():
    print("Exiting with code 0 - everything should be fine, right?")
    sys.exit(0)


def exit_code_one():
    print("Causing expected failure and exiting with code 1")
    sys.exit(1)


if __name__ == "__main__":
    exit_code_zero()
