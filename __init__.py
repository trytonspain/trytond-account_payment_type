# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
import payment_type
import party
import invoice


def register():
    Pool.register(
        payment_type.PaymentType,
        party.PartyAccountPaymentType,
        party.Party,
        invoice.Invoice,
        module='account_payment_type', type_='model')
