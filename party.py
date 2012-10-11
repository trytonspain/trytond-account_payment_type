#This file is part of account_payment_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Party']
__metaclass__ = PoolMeta

class Party:
    __name__ = 'party.party'

    customer_payment_type = fields.Property(fields.Many2One(
        'account.payment.type', string='Customer Payment type',
        help='Payment type of the customer.'))
    supplier_payment_type = fields.Property(fields.Many2One(
        'account.payment.type', string='Supplier Payment type',
        help='Payment type of the supplier.'))
