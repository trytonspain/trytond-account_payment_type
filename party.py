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

    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE')
    company = fields.Many2One('company.company', 'Company', ondelete='CASCADE')
    customer_payment_type = fields.Many2One('account.payment.type',
        'Customer Payment type')
    supplier_payment_type = fields.Many2One('account.payment.type',
        'Supplier Payment type')


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
    def get_payment_type(cls, parties, names):
        PartyAccountPaymentType = Pool().get('party.account.payment.type')
        company = Transaction().context.get('company')

        res = {}
        party_ids = [p.id for p in parties]
        for fname in names:
            res[fname] = {}.fromkeys(party_ids, None)

        party_account_payment_type = PartyAccountPaymentType.search([
                ('company', '=', company),
                ('party', 'in', parties)
                ])
        for payment_type_fields in party_account_payment_type:
            party_id = payment_type_fields.party.id
            for fname in set(names):
                res[fname][party_id] = getattr(payment_type_fields, fname)
        return res

    @classmethod
    def set_payment_type(cls, parties, name, value):
        PartyAccountPaymentType = Pool().get('party.account.payment.type')
        company = Transaction().context.get('company')

        party_payment_types = PartyAccountPaymentType.search([
                ('company', '=', company),
                ('party', 'in', parties)
                ])
        PartyAccountPaymentType.write(party_payment_types, {name: value})

        vlist = []
        parties_done_ids = [papt.party.id for papt in party_payment_types]
        for missing_party_id in set(p.id
                for p in parties if p.id not in parties_done_ids):
            vlist.append({
                    'party': missing_party_id,
                    'company': company,
                    name: value,
                    })
        if vlist:
            PartyAccountPaymentType.create(vlist)
