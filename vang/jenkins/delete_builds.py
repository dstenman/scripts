#!/usr/bin/env python3

import argparse
from sys import argv

from vang.jenkins.api import call


def delete_builds(job_names):
    return [(job_name, call(
        f'/job/{job_name}/doDelete',
        method='POST',
        only_response_code=True,
    )) for job_name in job_names]


def parse_args(args):
    parser = argparse.ArgumentParser(description='Delete Jenkins jobs')
    parser.add_argument(
        'job_names',
        nargs='+',
        help='Jenkins job names',
    )
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])
    for job_name, response_code in delete_builds(args.job_names):
        print(job_name, response_code)
