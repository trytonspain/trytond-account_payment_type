# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
try:
    from trytond.modules.account_payment_type.tests.test_account_payment_type import suite
except ImportError:
    from .test_account_payment_type import suite

__all__ = ['suite']
