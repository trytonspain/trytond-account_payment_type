# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import move
from . import payment_type
from . import party
from . import invoice


def register():
    Pool.register(
        move.Move,
        move.Line,
        payment_type.PaymentType,
        party.PartyAccountPaymentType,
        party.Party,
        invoice.Invoice,
        module='account_payment_type', type_='model')
