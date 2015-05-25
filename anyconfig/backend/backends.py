#
# Copyright (C) 2011 - 2015 Satoru SATOH <ssato @ redhat.com>
# License: MIT
#
"""A module to aggregate config parser (loader/dumper) backends.
"""
from __future__ import absolute_import

import itertools
import logging
import operator
import pkg_resources

import anyconfig.compat
import anyconfig.utils

import anyconfig.backend.ini
import anyconfig.backend.json
import anyconfig.backend.xml

LOGGER = logging.getLogger(__name__)
PARSERS = [anyconfig.backend.ini.Parser, anyconfig.backend.json.Parser,
           anyconfig.backend.xml.Parser]

try:
    import anyconfig.backend.yaml_
    PARSERS.append(anyconfig.backend.yaml_.Parser)
except ImportError:
    LOGGER.warn("YAML module is not available. Disabled its support.")


for e in pkg_resources.iter_entry_points("anyconfig_backends"):
    try:
        PARSERS.append(e.load())
    except ImportError:
        continue


def cmp_cps(lhs, rhs):
    """Compare config parsers by these priorities.
    """
    return anyconfig.compat.cmp(lhs.priority(), rhs.priority())


def fst(tpl):
    """
    >>> fst((0, 1))
    0
    """
    return tpl[0]


def snd(tpl):
    """
    >>> snd((0, 1))
    1
    """
    return tpl[1]


def groupby_key(xs, kf):
    """An wrapper around itertools.groupby
    """
    return itertools.groupby(sorted(xs, key=kf), key=kf)


def uniq(iterable):
    """
    >>> uniq([1, 2, 3, 1, 2])
    [1, 2, 3]
    """
    acc = []
    for x in iterable:
        if x not in acc:
            acc.append(x)

    return acc


def list_parsers_by_type(cps=None):
    """
    :return: List (generator) of (config_type, [config_parser])
    """
    if cps is None:
        cps = PARSERS

    return ((t, sorted(p, key=operator.methodcaller("priority"))) for t, p
            in groupby_key(cps, operator.methodcaller("type")))


def _list_xppairs(xps):
    """List config parsers by priority.
    """
    return sorted((snd(xp) for xp in xps),
                  key=operator.methodcaller("priority"))


def list_parsers_by_extension(cps=None):
    """
    :return: List (generator) of (config_ext, [config_parser])
    """
    if cps is None:
        cps = PARSERS

    cps_by_ext = anyconfig.utils.concat(([(x, p) for x in p.extensions()] for p
                                         in cps))

    return ((x, _list_xppairs(xps)) for x, xps in groupby_key(cps_by_ext, fst))


def find_by_file(config_file, cps=None):
    """
    Find config parser by file's extension.

    :param config_file: Config file path
    """
    if cps is None:
        cps = PARSERS

    ext = anyconfig.utils.get_file_extension(config_file)
    for x, ps in list_parsers_by_extension(cps):
        if x == ext:
            return ps[-1]

    return None


def find_by_type(cptype, cps=None):
    """
    Find config parser by file's extension.

    :param cptype: Config file's type
    """
    if cps is None:
        cps = PARSERS

    for t, ps in list_parsers_by_type(cps):
        if t == cptype:
            return ps[-1]

    return None


def list_types(cps=None):
    """List available config types.
    """
    if cps is None:
        cps = PARSERS

    return sorted(uniq(t for t, ps in list_parsers_by_type(cps)))

# vim:sw=4:ts=4:et:
