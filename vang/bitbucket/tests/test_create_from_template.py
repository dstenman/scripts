#!/usr/bin/env python3
from argparse import Namespace
from unittest.mock import patch, call

from vang.bitbucket.create_from_template import commit_all
from vang.bitbucket.create_from_template import create_and_push_to_dest_repo
from vang.bitbucket.create_from_template import main
from vang.bitbucket.create_from_template import parse_args
from vang.bitbucket.create_from_template import setup as bitbucket_setup
from vang.bitbucket.create_from_template import update


@patch(
    'vang.bitbucket.create_from_template.get_clone_urls',
    autospec=True,
    return_value=[[
        '_',
        'project',
        'repo',
        'clone_url',
    ]])
def test_setup(mock_get_clone_urls):
    # branch 'branch'
    with patch('vang.bitbucket.create_from_template.run_command'
               ) as mock_run_command:
        assert ('clone_url',
                'work_dir/dest_project/dest_repo') == bitbucket_setup(
                    'project', 'repo', 'branch', 'dest_project', 'dest_repo',
                    'work_dir')
        assert [
            call('git clone -b branch clone_url work_dir/dest_project/dest_repo'
                 ),
            call(
                'rm -rf .git',
                cwd='work_dir/dest_project/dest_repo',
                return_output=True),
            call(
                'git init',
                cwd='work_dir/dest_project/dest_repo',
                return_output=True),
            call(
                'git checkout -b branch',
                cwd='work_dir/dest_project/dest_repo',
                return_output=True),
        ] == mock_run_command.mock_calls
    # branch 'master'
    with patch('vang.bitbucket.create_from_template.run_command'
               ) as mock_run_command:
        assert ('clone_url',
                'work_dir/dest_project/dest_repo') == bitbucket_setup(
                    'project', 'repo', 'master', 'dest_project', 'dest_repo',
                    'work_dir')
        assert [
            call('git clone -b master clone_url work_dir/dest_project/dest_repo'
                 ),
            call(
                'rm -rf .git',
                cwd='work_dir/dest_project/dest_repo',
                return_output=True),
            call(
                'git init',
                cwd='work_dir/dest_project/dest_repo',
                return_output=True),
        ] == mock_run_command.mock_calls


@patch('vang.bitbucket.create_from_template.run_command', autospec=True)
def test_commit_all(mock_run_command):
    commit_all('repo_dir')
    assert [
        call('git add --all', cwd='repo_dir', return_output=True),
        call(
            'git commit -m "Initial commit"',
            cwd='repo_dir',
            return_output=True),
    ] == mock_run_command.mock_calls


@patch('vang.bitbucket.create_from_template.rsr', autospec=True)
@patch(
    'vang.bitbucket.create_from_template._replace',
    autospec=True,
    return_value='_replace')
@patch(
    'vang.bitbucket.create_from_template.get_zipped_cases',
    autospec=True,
    return_value=[('repo', 'dest_repo')])
def test_update(mock_get_zipped_cases, mock__replace, mock_rsr):
    update('repo', 'dest_repo', 'dest_repo_dir')
    assert [call('repo', 'dest_repo', ['dest_repo_dir'],
                 '_replace')] == mock_rsr.mock_calls


@patch(
    'vang.bitbucket.create_from_template.set_repo_default_branch',
    autospec=True)
@patch(
    'vang.bitbucket.create_from_template.enable_repo_web_hook',
    autospec=True)
@patch('vang.bitbucket.create_from_template.run_command', autospec=True)
@patch(
    'vang.bitbucket.create_from_template.create_repo',
    autospec=True,
    return_value={'links': {
        'clone': [{
            'href': 'dest_repo_origin'
        }]
    }})
def test_create_and_push_to_dest_repo(mock_create_repo, mock_run_command,
                                      mock_enable_repo_web_hook,
                                      mock_set_repo_default_branch):
    # No webhook
    assert 'dest_repo_origin' == create_and_push_to_dest_repo(
        'branch', 'dest_project', 'dest_repo', 'dest_repo_dir')
    assert [call('dest_project', 'dest_repo')] == mock_create_repo.mock_calls
    assert 0 == mock_enable_repo_web_hook.call_count
    assert [
        call(
            'git remote add origin dest_repo_origin',
            cwd='dest_repo_dir',
            return_output=True),
        call(
            'git push -u origin branch',
            cwd='dest_repo_dir',
            return_output=True)
    ] == mock_run_command.mock_calls
    assert [call(('dest_project', 'dest_repo'),
                 'branch')] == mock_set_repo_default_branch.mock_calls
    # webhook
    assert 'dest_repo_origin' == create_and_push_to_dest_repo(
        'branch', 'dest_project', 'dest_repo', 'dest_repo_dir', 'webhook')
    assert [call(['dest_project', 'dest_repo'],
                 'webhook')] == mock_enable_repo_web_hook.mock_calls


@patch('builtins.print', autospec=True)
@patch(
    'vang.bitbucket.create_from_template.create_and_push_to_dest_repo',
    autospec=True,
    return_value='dest_repo_origin')
@patch('vang.bitbucket.create_from_template.commit_all', autospec=True)
@patch('vang.bitbucket.create_from_template.update', autospec=True)
@patch(
    'vang.bitbucket.create_from_template.setup',
    autospec=True,
    return_value=['clone_url', 'dest_repo_dir'])
def test_main(mock_setup, mock_update, mock_commit_all,
              mock_create_and_push_to_dest_repo, mock_print):
    main('project', 'repo', 'branch', 'dest_project', 'dest_repo', 'work_dir',
         'webhook')
    assert [
        call('project', 'repo', 'branch', 'dest_project', 'dest_repo',
             'work_dir')
    ] == mock_setup.mock_calls
    assert [call('repo', 'dest_repo',
                 'dest_repo_dir')] == mock_update.mock_calls
    assert [call('dest_repo_dir')] == mock_commit_all.mock_calls
    assert [
        call('branch', 'dest_project', 'dest_repo', 'dest_repo_dir', 'webhook')
    ] == mock_create_and_push_to_dest_repo.mock_calls
    assert [call('Created', 'dest_repo_origin')] == mock_print.mock_calls


def test_parse_args():
    # defaults
    assert Namespace(
        branch='develop',
        dest_project='dest_project',
        dest_repo='dest_repo',
        dir='.',
        src_project='src_project',
        src_repo='src_repo',
        webhook=False) == parse_args(
            ['src_project', 'src_repo', 'dest_project', 'dest_repo'])
    # no defaults
    assert Namespace(
        branch='branch',
        dest_project='dest_project',
        dest_repo='dest_repo',
        dir='dir',
        src_project='src_project',
        src_repo='src_repo',
        webhook='webhook') == parse_args([
            'src_project', 'src_repo', 'dest_project', 'dest_repo', '-b',
            'branch', '-d', 'dir', '-w', 'webhook'
        ])