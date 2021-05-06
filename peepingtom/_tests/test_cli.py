import sys

from peepingtom.__main__ import parse


def test_cli_parse():
    args = parse('peep test.mrc test.star -m bunch -n reg'.split())
    args.paths = ['test.mrc', 'test.star']
    assert args.mode == 'bunch'
    assert args.name_regex == 'reg'
    assert args.recursive is False
    assert args.dry_run is False
    assert args.strict is False
