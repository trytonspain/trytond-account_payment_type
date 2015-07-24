# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, If, Not
from trytond.transaction import Transaction

__all__ = ['Invoice']
__metaclass__ = PoolMeta


class Invoice:
    __name__ = 'account.invoice'
    payment_type = fields.Many2One('account.payment.type', 'Payment Type',
        domain=[
            If(Eval('type').in_(['out_invoice', 'in_credit_note']),
            ('kind', '=', 'receivable'),
            ('kind', '=', 'payable')),
            ],
        states={
            'readonly': Not(Bool(Eval('state').in_(['draft', 'validated']))),
            }, depends=['state', 'type'])

    def __get_payment_type(self, party=None, type=None, company=None):
        '''
        Return default account payment type
        '''
        res = {}
        if party is None:
            party = self.party
        if type is None:
            type = self.type
        if company is None:
            company = self.company
        if party:
            if type == 'out_invoice' \
                    and party.customer_payment_type:
                res['payment_type'] = party.customer_payment_type.id
            elif type == 'in_invoice' \
                    and party.supplier_payment_type:
                res['payment_type'] = party.supplier_payment_type.id
        else:
            res['payment_type'] = None
        if company and type in ('out_credit_note', 'in_credit_note'):
            if type == 'out_credit_note' \
                    and company.customer_payment_type:
                res['payment_type'] = company.customer_payment_type.id
            elif type == 'in_credit_note' \
                    and company.supplier_payment_type:
                res['payment_type'] = company.supplier_payment_type.id
        return res

    def on_change_party(self):
        res = super(Invoice, self).on_change_party()
        res.update(self.__get_payment_type())
        return res

    def _get_move_line(self, date, amount):
        res = super(Invoice, self)._get_move_line(date, amount)
        if self.payment_type:
            res['payment_type'] = self.payment_type
        return res

    @classmethod
    def compute_default_payment_type(cls, values):
        pool = Pool()
        Party = pool.get('party.party')
        Company = pool.get('company.company')
        changes = {}
        if ('payment_type' not in values and 'party' in values
                and 'type' in values):
            party = Party(values['party'])
            company = Company(values.get('company',
                    Transaction().context.get('company')))
            changes.update(cls().__get_payment_type(party=party,
                    company=company, type=values.get('type')))
            # Compatibility with account_bank module
            if hasattr(cls, 'compute_default_bank_account'):
                new_values = values.copy()
                new_values.update(changes)
                changes.update(cls.compute_default_bank_account(new_values))
        return changes

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            values.update(cls.compute_default_payment_type(values))
        return super(Invoice, cls).create(vlist)
