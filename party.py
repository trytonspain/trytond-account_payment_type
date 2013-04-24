# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contain
# the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction

__all__ = ['PartyAccountPaymentType', 'Party']
__metaclass__ = PoolMeta


class PartyAccountPaymentType(ModelSQL, ModelView):
    'Party Account Payment Type'
    __name__ = 'party.account.payment.type'

    customer_payment_type = fields.Many2One('account.payment.type',
        'Customer Payment type')
    supplier_payment_type = fields.Many2One('account.payment.type',
        'Supplier Payment type')
    company = fields.Many2One('company.company', 'Company')
    party = fields.Many2One('party.party', 'Party')


class Party:
    __name__ = 'party.party'

    customer_payment_type = fields.Function(fields.Many2One(
        'account.payment.type', 'Customer Payment type', domain=[
                ('kind', '=', 'receivable'),
                ],
            help='Payment type of the customer.'),
        'get_payment_type', setter='set_payment_type')
    supplier_payment_type = fields.Function(fields.Many2One(
        'account.payment.type', string='Supplier Payment type', domain=[
                ('kind', '=', 'payable'),
                ],
        help='Payment type of the supplier.'),
        'get_payment_type', setter='set_payment_type')

    @classmethod
    def get_payment_type(self, parties, names):
        res = {}
        PartyAccountPaymentType = Pool().get('party.account.payment.type')
        company = Transaction().context.get('company')
        party = parties[0].id
        party_account_payment_type = False
        if company:
            party_account_payment_type = PartyAccountPaymentType.search([
                    ('company', '=', company),
                    ('party', '=', party)
                    ], limit=1)
            if party_account_payment_type:
                for field_name in set(names):
                    value = getattr(party_account_payment_type[0], field_name)
                    if value:
                        res[field_name] = {party: value.id}
                    else:
                        res[field_name] = {party: False}
        if not company or not party_account_payment_type:
            for field_name in set(names):
                res[field_name] = {party: False}
        return res

    @classmethod
    def set_payment_type(cls, parties, name, value):
        PartyAccountPaymentType = Pool().get('party.account.payment.type')
        company = Transaction().context.get('company')
        party = parties[0]
        if company:
            party_account_payment_type = PartyAccountPaymentType.search([
                    ('company', '=', company),
                    ('party', '=', party.id)
                    ], limit=1)
            if not party_account_payment_type:
                vlist = [{
                        'company': company,
                        'party': party.id,
                        name: value,
                        }]
                PartyAccountPaymentType.create(vlist)
            else:
                ids = party_account_payment_type[0]
                PartyAccountPaymentType.write([ids], {name: value})
