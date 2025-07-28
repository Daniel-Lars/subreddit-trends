import sys


def exit_code_zero():
    print("Exiting with code 0")
    sys.exit(0)


def exit_code_one():
    print("Causing expected failure and exiting with code 1")
    sys.exit(1)


if __name__ == "__main__":
    # Test exit with code 1
    exit_code_one()
