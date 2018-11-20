#!/usr/bin/env python3

import argparse
from sys import argv

from vang.jenkins.api import call

FAILURE = 'FAILURE'
SUCCESS = 'SUCCESS'


def map_color(color):
    return SUCCESS if color == 'blue' else FAILURE


def get_jobs(statuses=(FAILURE, SUCCESS), only_names=False):
    jobs = call('/api/json')['jobs']
    return [
        job['name'] if only_names else job for job in jobs
        if map_color(job['color']) in statuses
    ]


def parse_args(args):
    parser = argparse.ArgumentParser(description='Get Jenkins jobs')
    parser.add_argument('-n', '--only_names', action='store_true', help='Get only job names')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-f',
        '--only_failures',
        action='store_true',
        help='Only failure jobs',
    )
    group.add_argument(
        '-s',
        '--only_successes',
        action='store_true',
        help='Only success jobs',
    )
    return parser.parse_args(args)


def main(only_failures, only_successes, only_names):
    if only_failures:
        job_statuses = [FAILURE]
    elif only_successes:
        job_statuses = [SUCCESS]
    else:
        job_statuses = [FAILURE, SUCCESS]

    for a_job in get_jobs(job_statuses, only_names):
        print(a_job)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
