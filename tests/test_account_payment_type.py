#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import datetime
from decimal import Decimal
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.transaction import Transaction
from trytond.tests.test_tryton import test_view, test_depends
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT


class AccountPaymentTypeTestCase(unittest.TestCase):
    'Test AccountPaymentType module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_payment_type')
        self.account_template = POOL.get('account.account.template')
        self.tax_code_template = POOL.get('account.tax.code.template')
        self.tax_template = POOL.get('account.tax.code.template')
        self.account = POOL.get('account.account')
        self.account_create_chart = POOL.get(
            'account.create_chart', type='wizard')
        self.company = POOL.get('company.company')
        self.user = POOL.get('res.user')
        self.fiscalyear = POOL.get('account.fiscalyear')
        self.sequence = POOL.get('ir.sequence')
        self.sequence_strict = POOL.get('ir.sequence.strict')
        self.move = POOL.get('account.move')
        self.move_line = POOL.get('account.move.line')
        self.payment_type = POOL.get('account.payment.type')
        self.journal = POOL.get('account.journal')
        self.account_type = POOL.get('account.account.type')

    def test0005views(self):
        'Test views'
        test_view('account_payment_type')

    def test0006depends(self):
        'Test depends'
        test_depends()

    def test0010move_lines(self):
        'Test account debit/credit'
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT):
            company, = self.company.search([('rec_name', '=', 'Dunder Mifflin')])
            fiscalyear, = self.fiscalyear.search([])
            today = datetime.date.today()
            invoice_sequence, = self.sequence_strict.create([{
                        'name': '%s' % today.year,
                        'code': 'account.invoice',
                        'company': company.id,
                        }])
            fiscalyear.out_invoice_sequence = invoice_sequence
            fiscalyear.in_invoice_sequence = invoice_sequence
            fiscalyear.out_credit_note_sequence = invoice_sequence
            fiscalyear.in_credit_note_sequence = invoice_sequence
            fiscalyear.save()
            period = fiscalyear.periods[0]
            journal_revenue, = self.journal.search([
                    ('code', '=', 'REV'),
                    ])
            revenue, = self.account.search([
                    ('kind', '=', 'revenue'),
                    ])
            receivable, = self.account.search([
                    ('kind', '=', 'receivable'),
                    ])
            payable, = self.account.search([
                    ('kind', '=', 'payable'),
                    ])
            payment_payable, = self.payment_type.create([{
                'name': 'Payment Payable',
                'kind': 'payable',
                'company': company.id,
                }])
            payment_receivable, = self.payment_type.create([{
                'name': 'Payment Receivable',
                'kind': 'receivable',
                'company': company.id,
                }])
            move, = self.move.create([{
                    'period': period.id,
                    'journal': journal_revenue.id,
                    'date': period.start_date,
                    }])
            self.move_line.create([{
                    'move': move.id,
                    'account': revenue.id,
                    'debit': Decimal(30),
                    }])
            self.assertRaises(Exception, self.move_line.create, [{
                    'move': move.id,
                    'account': revenue.id,
                    'debit': Decimal(30),
                    'payment_type': payment_receivable,
                    }])
            # TODO Create move line payment + payment type payable


def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.account.tests import test_account
    for test in test_account.suite():
        if test not in suite and not isinstance(test, doctest.DocTestCase):
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPaymentTypeTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
