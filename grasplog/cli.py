import logging
import sys
from argparse import ArgumentParser
from typing import List

import grasplog.ml.clustering
from grasplog import __version__
from grasplog.datamodel import AppContext
from grasplog.datamodel import OutputFormat
from grasplog.exception import GraspLogException, InvalidCmdLineArgException
from grasplog.ui_helper import print_err
from grasplog.file_reader import read_events_from_glob


def create_app_config(args: List[str]) -> AppContext:
    parser = ArgumentParser(
        description="Read log file(s) and organize similar log events into clusters for easier review."
    )

    parser.add_argument(
        "path_glob",
        metavar="PATH",
        help="Logs path, can be a file, directory or glob pattern. "
             "Examples: 'syslog', './syslog.4.gz', '/var/log', '/var/log/syslog*', '/var/log/**/*'",
    )

    parser.add_argument(
        "--max-distance",
        metavar="MAX_DISTANCE",
        type=float,
        help=f"Max cosine distance between two log events to be considered as the same cluster. "
             "Allowed values range between 0 and 1. "
             "0 means log events have to be the same to end up in the same cluster. "
             "1 means all log events end up in the same cluster. "
             f"Default value: {AppContext.DEFAULT_MAX_DISTANCE}",
        default=AppContext.DEFAULT_MAX_DISTANCE,
    )

    parser.add_argument(
        "--max-samples-per-cluster",
        metavar="MAX_SAMPLES_PER_CLUSTER",
        type=int,
        help="How many items per detected cluster should be displayed",
        default=5,
    )

    parser.add_argument(
        "--max-noisy-samples",
        metavar="MAX_NOISY_SAMPLES",
        type=int,
        help="Number of noisy samples to be displayed. Defaults to MAX_SAMPLES_PER_CLUSTER",
    )

    parser.add_argument(
        "--output-format",
        default=OutputFormat.pretty_format,
        type=OutputFormat,
        choices=list(OutputFormat),
        help="Human readable output by default",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print verbose debug messages to stderr"
    )

    parser.add_argument("--version", action="version", version=__version__)

    parsed_args = parser.parse_args(args)
    path_glob: str = parsed_args.path_glob
    max_distance: float = parsed_args.max_distance
    max_samples_per_cluster: int = parsed_args.max_samples_per_cluster
    max_noisy_samples: int = parsed_args.max_noisy_samples or max_samples_per_cluster
    output_format: OutputFormat = parsed_args.output_format
    debug_mode: bool = parsed_args.debug

    if max_distance <= 0:
        raise InvalidCmdLineArgException(f"MAX_DISTANCE argument must be greater than 0, "
                                         f"floating point numbers are allowed "
                                         f"(e.g. '{AppContext.DEFAULT_MAX_DISTANCE}')")
    if max_samples_per_cluster < 1:
        raise InvalidCmdLineArgException("MAX_SAMPLES_PER_CLUSTER argument must be an integer greater than 1")
    if max_noisy_samples < 1:
        raise InvalidCmdLineArgException("MAX_NOISY_SAMPLES argument must be an integer greater than 1")

    return AppContext(
        path_glob=path_glob,
        max_distance=max_distance,
        max_samples_per_cluster=max_samples_per_cluster,
        max_noisy_samples=max_noisy_samples,
        output_format=output_format,
        debug_mode=debug_mode,
    )


def setup_loging(debug_mode: bool):
    log_level = logging.DEBUG if debug_mode else logging.INFO
    # All logs are going to stderr not to conflict with normal program output
    logging.basicConfig(stream=sys.stderr, level=log_level)


def main():
    try:
        app_config = create_app_config(sys.argv[1:])
        setup_loging(app_config.debug_mode)
        event_iterator = read_events_from_glob(app_config.path_glob)
        accumulator = grasplog.ml.clustering.process(
            event_iterator=event_iterator,
            max_samples_per_cluster=app_config.max_samples_per_cluster,
            max_noisy_samples=app_config.max_noisy_samples,
            max_distance=app_config.max_distance,
        )
        accumulator.output(app_config.output_format)
    except GraspLogException as e:
        print_err(str(e))
        sys.exit(1)
