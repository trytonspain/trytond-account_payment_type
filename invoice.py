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

    def __get_payment_type(self):
        '''
        Return default account payment type
        '''
        if self.party:
            if self.type == 'out_invoice' \
                    and self.party.customer_payment_type:
                self.payment_type = self.party.customer_payment_type
            elif self.type == 'in_invoice' \
                    and self.party.supplier_payment_type:
                self.payment_type = self.party.supplier_payment_type

        if self.company and not self.payment_type:
            if self.type == 'out_invoice' \
                    and self.company.party.customer_payment_type:
                self.payment_type = self.company.party.customer_payment_type
            if self.type == 'in_invoice' \
                    and self.company.party.supplier_payment_type:
                self.payment_type = self.company.party.supplier_payment_type
            if self.type == 'out_credit_note' \
                    and self.company.party.supplier_payment_type:
                self.payment_type = self.company.party.supplier_payment_type
            elif self.type == 'in_credit_note' \
                    and self.company.party.customer_payment_type:
                self.payment_type = self.company.party.customer_payment_type

    @fields.depends('party', 'payment_type', 'company', 'type')
    def on_change_party(self):
        super(Invoice, self).on_change_party()
        self.__get_payment_type()

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

        payment_type = values.get('payment_type')
        party = values.get('party')
        _type = values.get('type')
        company = values.get('company', Transaction().context.get('company'))

        changes = {}
        if not payment_type and party and _type and company:
            invoice = cls()
            invoice.party = Party(party)
            invoice.type = _type
            invoice.company = Company(company)
            invoice.payment_type = None
            invoice.__get_payment_type()
            changes['payment_type'] = invoice.payment_type

        return changes

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            values.update(cls.compute_default_payment_type(values))
        return super(Invoice, cls).create(vlist)
