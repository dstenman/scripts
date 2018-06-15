import unittest
from unittest.mock import patch

from artifactory_utils import *


@patch('artifactory_utils.glob')
@patch('artifactory_utils.exists')
def test_get_pom_path(mock_exists, mock_glob):
    mock_exists.return_value = True
    assert '/foo/bar/pom.xml' == get_pom_path('/foo/bar')
    mock_exists.assert_called_with('/foo/bar/pom.xml')

    mock_exists.return_value = False
    mock_glob.return_value = ['/foo/bar/foo.pom']
    assert '/foo/bar/foo.pom' == get_pom_path('/foo/bar')

    mock_glob.return_value = [
        '/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-20150610.210152-141.pom',
        '/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-SNAPSHOT.pom'
    ]
    assert '/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-SNAPSHOT.pom' == get_pom_path(
        '/signing.updatesigning/1.0.0-SNAPSHOT')

    # mock_glob.return_value = []
    # self.assertRaises(ValueError, get_pom_path, '/foo/bar')


def test_get_artifact_base_uri():
    assert '/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT' == get_artifact_base_uri(
        'repo',
        'com.foo.bar',
        'business.baz',
        '1.0.0-SNAPSHOT',
    )
