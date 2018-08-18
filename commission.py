# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import PoolMeta
__all__ = ['Commission']

class Commission(metaclass=PoolMeta):
    __name__ = 'commission'

    @classmethod
    def _get_invoice(cls, key):
        invoice = super(Commission, cls)._get_invoice(key)
        agent = key['agent']
        if key['type'] == 'out':
            payment_type = agent.party.customer_payment_type
        else:
            payment_type = agent.party.supplier_payment_type
        if payment_type:
            invoice.payment_type = payment_type
        return invoice
