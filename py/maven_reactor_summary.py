#!/usr/bin/env python3

import re
from glob import glob
from itertools import chain

from os.path import realpath


def get_reactor_summary(mvn_log_file):
    """ Returns reactor summary. """
    start = False
    lines = []
    with open(mvn_log_file, 'rt', encoding='utf-8') as mvn_log:
        for line in mvn_log:
            if re.match(r'.*Reactor Summary.*', line):
                start = True
            if start and re.match(r'^.INFO. -', line):
                break
            if start:
                lines.append(line.strip())
    return lines[2:-1]


def get_project(line):
    """ Returns project of reactor line. """
    start = re.search(r' ', line).end()
    end = re.search(r' \.', line).start()
    return line[start:end]


def get_successes(reactor_summary):
    """ Returns success projects """
    return [get_project(l) for l in reactor_summary if re.search('SUCCESS', l)]


def get_failures(reactor_summary):
    """ Returns failure projects """
    return [get_project(l) for l in reactor_summary if not re.search('SUCCESS', l)]


def get_summary(mvn_log_files, do_print=False):
    summaries = tuple(chain.from_iterable([get_reactor_summary(log_file) for log_file in mvn_log_files]))
    result = get_successes(summaries), get_failures(summaries)
    if do_print:
        print_summary(*result)
    return result


def print_summary(successes, failures):
    length = 80
    lines = []

    def banner(text='', fill=' '):
        s = ' ' + text + ' ' if text else text
        l = int(length / 2 + len(s) / 2)
        return s.rjust(l, fill).ljust(length, fill)

    def artifact(id, success, fill='.'):
        outcome = 'SUCCESS' if success else 'FAILURE'
        return id + outcome.rjust(length - len(id), fill)

    for text in ('', 'Summary', ''):
        lines.append(banner(text, '*'))
    for id in sorted(successes):
        lines.append(artifact(id, True))
    for id in sorted(failures):
        lines.append(artifact(id, False))
    for text in ('',):
        lines.append(banner(text, '*'))

    print('\n'.join(lines))


def main(roots, log_file_name):
    successes, failures = get_summary([realpath(p) for root in roots
                                       for p in glob("{}/**/{}".format(root, log_file_name), recursive=True)])
    print_summary(successes, failures)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Prints reactor summary of Maven build log files')
    parser.add_argument('-d', '--dirs', help='Root directory in which to find Maven log files', default=['.'])
    parser.add_argument('-l', '--log', help='Name of Maven build log file(s)', default='mvn.log')
    args = parser.parse_args()

    main(args.dirs, args.log)