#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import argv

from vang.tfs.clone_repos import clone_repos
from vang.tfs.create_repo import create_repo
from vang.misc.s import get_zipped_cases
from vang.pio.rsr import _replace, rsr
from vang.pio.shell import run_command


def setup(repo, branch, dest_repo, work_dir):
    clone_url, repo_dir = clone_repos(
        work_dir,
        repos=[repo],
        branch=branch,
    )[0]

    dest_repo_dir = f'{work_dir}/{dest_repo}'
    run_command(f'mv {repo_dir} {dest_repo_dir}')

    run_command('rm -rf .git', return_output=True, cwd=dest_repo_dir)
    run_command('git init', return_output=True, cwd=dest_repo_dir)
    if not branch == 'master':
        run_command(
            f'git checkout -b {branch}',
            return_output=True,
            cwd=dest_repo_dir,
        )
    return clone_url, dest_repo_dir


def commit_all(repo_dir):
    run_command('git add --all', return_output=True, cwd=repo_dir)
    run_command(
        'git commit -m "Initial commit"',
        return_output=True,
        cwd=repo_dir,
    )


def update(repo, dest_repo, dest_repo_dir):
    for old, new in get_zipped_cases([repo, dest_repo]):
        rsr(
            old,
            new,
            [dest_repo_dir],
            _replace(False),
        )


def create_and_push_to_dest_repo(
        branch,
        dest_repo,
        dest_repo_dir,
):
    dest_repo_origin = create_repo(dest_repo)['remoteUrl']
    run_command(
        f'git remote add origin {dest_repo_origin}',
        return_output=True,
        cwd=dest_repo_dir)
    run_command(
        f'git push -u origin {branch}',
        return_output=True,
        cwd=dest_repo_dir,
    )
    return dest_repo_origin


def main(
        repo,
        branch,
        dest_repo,
        work_dir,
):
    clone_url, dest_repo_dir = setup(
        repo,
        branch,
        dest_repo,
        work_dir,
    )

    update(repo, dest_repo, dest_repo_dir)

    commit_all(dest_repo_dir)

    dest_repo_origin = create_and_push_to_dest_repo(
        branch,
        dest_repo,
        dest_repo_dir,
    )
    print('Created', dest_repo_origin)


def parse_args(args):
    parser = ArgumentParser(
        description='Create a new repo based on template'
        ' repo.\nExample: create_from_template PCS1906 foo PCS1906'
        ' bar -b develop -d .')
    parser.add_argument(
        'src_repo',
        help='The repo from which to create the new repo (must exist)'
        ', e.g. organisation/project/repo1',
    )
    parser.add_argument(
        'dest_repo',
        help='The new repo (must not exist), '
        'e.g. organisation/project/repo2',
    )
    parser.add_argument(
        '-b',
        '--branch',
        default='develop',
        help='The branch to use and create, e.g. develop. '
        'It will be set as default branch on created repo',
    )
    parser.add_argument(
        '-d',
        '--dir',
        default='.',
        help='The directory to create local repo in',
    )
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])
    main(
        args.src_repo,
        args.branch,
        args.dest_repo,
        args.dir,
    )
