# This file is part of the account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountPaymentTypeTestCase(ModuleTestCase):
    'Test Account Payment Type module'
    module = 'account_payment_type'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPaymentTypeTestCase))
    return suite