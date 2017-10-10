"""Tests of version string parsing, generation and comparison."""

import itertools
import unittest

import packaging.version
import pkg_resources
import semver

from version_query.version import Version
from .examples import \
    COMPATIBLE_CASES, INCOMPATIBLE_CASES, case_to_version_tuple, INCREMENT_CASES, \
    COMPARISON_CASES_LESS, COMPARISON_CASES_EQUAL


class Tests(unittest.TestCase):

    maxDiff = None

    def test_from_str(self):
        for version_str, (args, kwargs) in itertools.chain(
                COMPATIBLE_CASES.items(), INCOMPATIBLE_CASES.items()):
            version_tuple = case_to_version_tuple(args, kwargs)
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                self.assertEqual(Version.from_str(version_str).to_tuple(), version_tuple)

    def test_from_str_bad(self):
        with self.assertRaises(ValueError):
            Version.from_str('hello world')

    def test_from_py_version(self):
        for version_str, (args, kwargs) in COMPATIBLE_CASES.items():
            version_tuple = case_to_version_tuple(args, kwargs)
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                py_version = packaging.version.Version(version_str)
                self.assertEqual(Version.from_py_version(py_version).to_tuple(),
                                 version_tuple, py_version)
                py_version_setuptools = pkg_resources.parse_version(version_str)
                self.assertEqual(Version.from_py_version(py_version_setuptools).to_tuple(),
                                 version_tuple, py_version_setuptools)

    def test_from_sem_version(self):
        for version_str, (args, kwargs) in COMPATIBLE_CASES.items():
            version_tuple = case_to_version_tuple(args, kwargs)
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
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
            Version(5, pre_release=[(None, 'dev', -1)]).to_str()
        with self.assertRaises(ValueError):
            Version(1, patch=13).to_str()
