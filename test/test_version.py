"""Tests of version string parsing and generation."""

import itertools
import unittest

import packaging.version
import pkg_resources
import semver

from version_query.version import VersionComponent, Version
from .examples import \
    KWARG_NAMES, COMPATIBLE_CASES, INCOMPATIBLE_CASES, INCREMENT_CASES, COMPARISON_CASES_LESS, \
    COMPARISON_CASES_EQUAL

from version_query.version import VersionOld

OLD_CASES = {
    '0': ((0,), {}),
    '42': ((42,), {}),
    '5+d2a610ba': ((5,), {'commit_sha': 'd2a610ba'}),
    '0.1': ((0, 1), {}),
    '8.0': ((8, 0), {}),
    '16.4': ((16, 4), {}),
    '5.0+f753199e': ((5, 0), {'commit_sha': 'f753199e'}),
    '0.54.0': ((0, 54, 0), {}),
    '1.0.0': ((1, 0, 0), {}),
    '7.0.42+1d7b090a': ((7, 0, 42), {'commit_sha': '1d7b090a'}),
    '1.0.0.4': ((1, 0, 0, None, 4), {}),
    '2.0.0.8+cc81cee': ((2, 0, 0, None, 8, 'cc81cee'), {}),
    '4.5.0.dev': ((4, 5, 0, 'dev'), {}),
    '1.0.0.rc3': ((1, 0, 0, 'rc', 3), {}),
    '1.0.1.dev0': ((1, 0, 1, 'dev', 0), {}),
    '0.4.4.dev5+84e1d430': ((0, 4, 4, 'dev', 5, '84e1d430'), {})}

OLD_KWARG_NAMES = ('major', 'minor', 'release', 'suffix', 'patch', 'commit_sha')


class TestsOld(unittest.TestCase):

    def test_version_parse(self):
        for version_str, (args, kwargs) in OLD_CASES.items():
            version_tuple = tuple([
                args[i] if i < len(args)
                else (kwargs[OLD_KWARG_NAMES[i]] if OLD_KWARG_NAMES[i] in kwargs else None)
                for i in range(len(OLD_KWARG_NAMES))])
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                self.assertEqual(VersionOld.parse_str(version_str), version_tuple)

    def test_version_parse_bad(self):
        with self.assertRaises(packaging.version.InvalidVersion):
            VersionOld.parse_str('hello world')

    def test_version_generate(self):
        for result, (args, kwargs) in OLD_CASES.items():
            with self.subTest(args=args, kwargs=kwargs, result=result):
                self.assertEqual(VersionOld.generate_str(*args, **kwargs), result)

    def test_version_generate_bad(self):
        with self.assertRaises(NotImplementedError):
            VersionOld.generate_str()
        with self.assertRaises(NotImplementedError):
            VersionOld.generate_str(5, patch=2)
        with self.assertRaises(NotImplementedError):
            VersionOld.generate_str(1, release=13)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_from_str(self):
        for version_str, (args, kwargs) in COMPATIBLE_CASES.items():
            version_tuple = args + tuple(
                v for k, v in sorted(kwargs.items(), key=lambda _: KWARG_NAMES.index(_[0])))
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                self.assertEqual(Version.from_str(version_str).to_tuple(), version_tuple)
                try:
                    py_version = packaging.version.Version(version_str)
                except ValueError:
                    pass
                else:
                    self.assertEqual(Version.from_py_version(py_version).to_tuple(),
                                     version_tuple, py_version)
                try:
                    py_version_setuptools = pkg_resources.parse_version(version_str)
                except ValueError:
                    pass
                else:
                    self.assertEqual(Version.from_py_version(py_version_setuptools).to_tuple(),
                                     version_tuple, py_version_setuptools)
                try:
                    sem_version = semver.parse(version_str)
                except ValueError:
                    pass
                else:
                    self.assertEqual(Version.from_sem_version(sem_version).to_tuple(),
                                     version_tuple, sem_version)
                try:
                    sem_version_info = semver.parse_version_info(version_str)
                except ValueError:
                    pass
                else:
                    self.assertEqual(Version.from_sem_version(sem_version_info).to_tuple(),
                                     version_tuple, sem_version_info)
        for version_str, (args, kwargs) in INCOMPATIBLE_CASES.items():
            version_tuple = args + tuple(
                v for k, v in sorted(kwargs.items(), key=lambda _: KWARG_NAMES.index(_[0])))
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                self.assertEqual(Version.from_str(version_str).to_tuple(), version_tuple)

    def test_from_str_bad(self):
        with self.assertRaises(ValueError):
            Version.from_str('hello world')

    def test_increment(self):
        for (initial_version, args), result_version in INCREMENT_CASES.items():
            with self.subTest(initial_version=initial_version, args=args,
                              result_version=result_version):
                self.assertEqual(Version.from_str(initial_version).increment(*args),
                                 Version.from_str(result_version))

    def test_compare(self):
        for earlier_version, later_version in COMPARISON_CASES_LESS.items():
            with self.subTest(earlier_version=earlier_version, later_version=later_version):
                self.assertLess(Version.from_str(earlier_version), Version.from_str(later_version))

        for version, equivalent_version in COMPARISON_CASES_EQUAL.items():
            with self.subTest(version=version, equivalent_version=equivalent_version):
                self.assertEqual(Version.from_str(version), Version.from_str(equivalent_version))

    def test_to_str(self):
        for result, (args, kwargs) in itertools.chain(
                COMPATIBLE_CASES.items(), INCOMPATIBLE_CASES.items()):
            with self.subTest(args=args, kwargs=kwargs, result=result):
                self.assertEqual(Version(*args, **kwargs).to_str(), result)

    def test_to_str_bad(self):
        with self.assertRaises(ValueError):
            Version(-1).to_str()
        with self.assertRaises(ValueError):
            Version(5, pre_release=[(None, 'dev',-1)]).to_str()
        with self.assertRaises(ValueError):
            Version(1, patch=13).to_str()
