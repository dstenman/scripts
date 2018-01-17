#!/usr/bin/env python3

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo, tag):
    return '/rest/api/1.0/projects/{}/repos/{}/tags?filterText={}'.format(project, repo, tag)


def get_tags(repo_specs, tag=''):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1], tag)
        yield spec, call(uri)


def main(tag='', dirs=['.'], repos=None):
    if args.repos:
        specs = (repo.split('/') for repo in repos)
    else:
        specs = (get_project_and_repo(get_clone_url(dir)) for dir in dirs)
    for spec, response in get_tags(specs, tag):
        print('{}/{}: {}'.format(spec[0], spec[1], [value['displayId'] for value in response['values']]))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get repository tags from Bitbucket')
    parser.add_argument('-t', '--tag',
                        help='Tag filter',
                        default='')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*',
                       help='Repos, e.g. key1/repo1 key2/repo2')
    args = parser.parse_args()

    main(args.tag, args.dirs, args.repos)