# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import Workflow, ModelView, fields
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
        res = {}
        if self.party:
            if self.type == 'out_invoice' \
                    and self.party.customer_payment_type:
                res['payment_type'] = self.party.customer_payment_type.id
            elif self.type == 'in_invoice' \
                    and self.party.supplier_payment_type:
                res['payment_type'] = self.party.supplier_payment_type.id
        else:
            res['payment_type'] = None
        if self.company and type in ('out_credit_note', 'in_credit_note'):
            if self.type == 'out_credit_note' \
                    and self.company.customer_payment_type:
                res['payment_type'] = self.company.customer_payment_type.id
            elif self.type == 'in_credit_note' \
                    and self.company.supplier_payment_type:
                res['payment_type'] = self.company.supplier_payment_type.id
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

    def get_cancel_move(self):
        with Transaction().set_context(cancel_move=True):
            return super(Invoice, self).get_cancel_move()

    @classmethod
    @ModelView.button
    @Workflow.transition('posted')
    def post(cls, invoices):
        Line = Pool().get('account.move.line')
        for invoice in invoices:
            if invoice.move and invoice.payment_type:
                for line in invoice.move.lines:
                    if line.account_kind == invoice.payment_type.kind:
                        vals = {'payment_type': invoice.payment_type}
                        Line.write([line], vals)
        super(Invoice, cls).post(invoices)
