import glob
import os
import gzip
from typing import Iterator, TextIO

from grasplog.exception import GraspLogException, GraspLogIOException
from grasplog.ui_helper import print_err


def read_events_from_glob(glob_path: str) -> Iterator[str]:
    file_count = 0
    line_count = 0
    for path in glob.iglob(glob_path, recursive=True):
        if (not os.path.exists(path)) or os.path.isdir(path):
            continue
        if not os.access(path, os.R_OK):
            print_err(f"Skipping file '{path}' - no read permissions")
            continue
        for line in _read_lines(path):
            line_count += 1
            yield line
        file_count += 1
    if file_count == 0:
        raise GraspLogException("No readable files detected. "
                                "To read multiple files, use glob patterns: 'dir/*' or 'dir/**/*.log'")
    if line_count == 0:
        raise GraspLogException("All files are empty")


def _open_file(path: str) -> TextIO:
    if path.endswith(".gz") or path.endswith(".gzip"):
        return gzip.open(path, "rt")
    else:
        return open(path, "rt")


def _read_lines(path: str) -> Iterator[str]:
    try:
        with _open_file(path) as handle:
            while line := handle.readline():
                yield line
    except UnicodeDecodeError:
        raise GraspLogIOException(f"Cannot read log events from file {path}. "
                                  f"Only plain and rotated (.gz) logs are currently supported.")
    except gzip.BadGzipFile:
        raise GraspLogException(f"File {path} is not a valid gzip archive.")
