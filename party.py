# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contain
# the full copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pool import PoolMeta, Pool
from trytond.modules.company.model import CompanyValueMixin

__all__ = ['PartyAccountPaymentType', 'Party']
customer_payment_type = fields.Many2One(
    'account.payment.type', 'Customer Payment type', domain=[
        ('kind', 'in', ['both', 'receivable']),
        ],
    help='Payment type of the customer.')
supplier_payment_type = fields.Many2One(
    'account.payment.type', string='Supplier Payment type', domain=[
        ('kind', 'in', ['both', 'payable']),
        ],
    help='Payment type of the supplier.')


class PartyAccountPaymentType(CompanyValueMixin, ModelSQL):
    'Party Account Payment Type'
    __name__ = 'party.account.payment.type'

    party = fields.Many2One('party.party', 'Party', ondelete='CASCADE')
    customer_payment_type = customer_payment_type
    supplier_payment_type = supplier_payment_type


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    customer_payment_type = fields.MultiValue(customer_payment_type)
    supplier_payment_type = fields.MultiValue(supplier_payment_type)
    payment_types = fields.One2Many('party.account.payment.type', 'party',
        "Payment Types")

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field in ['customer_payment_type', 'supplier_payment_type']:
            return pool.get('party.account.payment.type')
        return super(Party, cls).multivalue_model(field)
