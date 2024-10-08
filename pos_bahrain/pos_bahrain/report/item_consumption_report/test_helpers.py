# -*- coding: utf-8 -*-
# Copyright (c) 2018, 9t9it and Contributors
# See license.txt
from __future__ import unicode_literals
from frappe.utils import getdate
import unittest
from toolz import pluck

from pos_bahrain.pos_bahrain.report.item_consumption_report.helpers \
    import generate_intervals


class TestItemConsumptionReport(unittest.TestCase):
    def test_generate_intervals(self):
        actual = generate_intervals(None, '2012-12-12', '2012-12-12')
        expected = []
        self.assertEqual(actual, expected)

    def test_generate_intervals_weekly(self):
        actual = len(
            generate_intervals('Weekly', '2012-08-19', '2012-09-12')
        )
        expected = 5
        self.assertEqual(actual, expected)

    def test_generate_intervals_weekly_keys(self):
        actual = list(
            pluck(
                'key',
                generate_intervals('Weekly', '2012-08-19', '2012-09-12')
            )
        )
        expected = ['12W33', '12W34', '12W35', '12W36', '12W37']
        self.assertEqual(actual, expected)

    def test_generate_intervals_weekly_labels(self):
        actual = list(
            pluck(
                'label',
                generate_intervals('Weekly', '2012-08-19', '2012-08-24')
            )
        )
        expected = ['2012-08-13', '2012-08-20']
        self.assertEqual(actual, expected)

    def test_generate_intervals_weekly_start_dates(self):
        actual = list(
            pluck(
                'start_date',
                generate_intervals('Weekly', '2012-08-19', '2012-08-24')
            )
        )
        expected = [getdate('2012-08-13'), getdate('2012-08-20')]
        self.assertEqual(actual, expected)

    def test_generate_intervals_weekly_end_dates(self):
        actual = list(
            pluck(
                'end_date',
                generate_intervals('Weekly', '2012-08-19', '2012-08-24')
            )
        )
        expected = [getdate('2012-08-19'), getdate('2012-08-26')]
        self.assertEqual(actual, expected)

    def test_generate_intervals_monthly(self):
        actual = len(
            generate_intervals('Monthly', '2012-08-12', '2012-12-12')
        )
        expected = 5
        self.assertEqual(actual, expected)

    def test_generate_intervals_monthly_keys(self):
        actual = list(
            pluck(
                'key',
                generate_intervals('Monthly', '2012-12-12', '2013-03-19')
            )
        )
        expected = ['12M12', '13M01', '13M02', '13M03']
        self.assertEqual(actual, expected)

    def test_generate_intervals_monthly_labels(self):
        actual = list(
            pluck(
                'label',
                generate_intervals('Monthly', '2012-12-12', '2013-04-19')
            )
        )
        expected = ['Dec 12', 'Jan 13', 'Feb 13', 'Mar 13', 'Apr 13']
        self.assertEqual(actual, expected)

    def test_generate_intervals_monthly_start_dates(self):
        actual = list(
            pluck(
                'start_date',
                generate_intervals('Monthly', '2012-12-12', '2013-01-19')
            )
        )
        expected = [getdate('2012-12-01'), getdate('2013-01-01')]
        self.assertEqual(actual, expected)

    def test_generate_intervals_monthly_end_dates(self):
        actual = list(
            pluck(
                'end_date',
                generate_intervals('Monthly', '2012-12-12', '2013-01-19')
            )
        )
        expected = [getdate('2012-12-31'), getdate('2013-01-31')]
        self.assertEqual(actual, expected)

    def test_generate_intervals_yearly(self):
        actual = len(
            generate_intervals('Yearly', '2012-08-12', '2012-12-12')
        )
        expected = 1
        self.assertEqual(actual, expected)

    def test_generate_intervals_yearly_keys(self):
        actual = list(
            pluck(
                'key',
                generate_intervals('Yearly', '2012-12-12', '2013-03-19')
            )
        )
        expected = ['12Y', '13Y']
        self.assertEqual(actual, expected)

    def test_generate_intervals_yearly_labels(self):
        actual = list(
            pluck(
                'label',
                generate_intervals('Yearly', '2012-12-12', '2013-04-19')
            )
        )
        expected = ['2012', '2013']
        self.assertEqual(actual, expected)

    def test_generate_intervals_yearly_start_dates(self):
        actual = list(
            pluck(
                'start_date',
                generate_intervals('Yearly', '2012-12-12', '2013-01-19')
            )
        )
        expected = [getdate('2012-01-01'), getdate('2013-01-01')]
        self.assertEqual(actual, expected)

    def test_generate_intervals_yearly_end_dates(self):
        actual = list(
            pluck(
                'end_date',
                generate_intervals('Yearly', '2012-12-12', '2013-01-19')
            )
        )
        expected = [getdate('2012-12-31'), getdate('2013-12-31')]
        self.assertEqual(actual, expected)
