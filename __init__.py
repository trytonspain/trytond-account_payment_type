# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from .payment_type import *
from .party import *
from .invoice import *
from .move import *


def register():
    Pool.register(
        PaymentType,
        PartyAccountPaymentType,
        Party,
        Invoice,
        Move,
        Line,
        module='account_payment_type', type_='model')
