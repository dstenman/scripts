from datetime import datetime
from unittest.mock import patch

from vang.core.core import create_timestamp
from vang.core.core import has_match
from vang.core.core import is_included
from vang.core.core import pmap
from vang.core.core import pmap_unordered
from vang.core.core import select_keys


def test_create_timestamp():
    d = datetime(2007, 12, 6, 15, 29, 43, 79060)
    with patch('vang.core.core.datetime') as m:
        m.now.return_value = d
        assert '20071206T152943.079060' == create_timestamp()


def test_has_match():
    assert not has_match('foo', [])
    assert has_match('app.foo.bar', ['foo', 'app.*', 'bar'])
    assert not has_match('app.foo.bar', ['foo', '.*foox.*', 'bar'])


def test_is_included():
    assert is_included('foo', None, None)
    assert is_included('foo', ['bar'], None)
    assert not is_included('foo', ['f.*'], None)
    assert is_included('foo', None, ['foo'])
    assert is_included('foo', None, ['f.*'])
    assert is_included('foo', ['bar'], ['foo'])
    assert not is_included('foo', ['foo'], ['foo'])


def test_pmap():
    assert [2, 4, 6] == pmap(lambda x: x * 2, [1, 2, 3])


def test_pmap_unordered():
    assert [2, 4, 6] == sorted(pmap_unordered(lambda x: x * 2, [1, 2, 3]))


def test_select_keys():
    assert {
        'foo': 1,
        'bar': 2
    } == select_keys({
        'foo': 1,
        'bar': 2,
        'baz': 3
    }, ('foo', 'bar'))
