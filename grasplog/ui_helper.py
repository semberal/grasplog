import sys


def print_msg(msg: str):
    print(msg, flush=True)


def print_err(err_msg: str):
    print(f"Error: {err_msg}", file=sys.stderr, flush=True)
