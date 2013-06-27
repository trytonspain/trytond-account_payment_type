# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, If
from trytond.transaction import Transaction

__all__ = ['PaymentType']


class PaymentType(ModelSQL, ModelView):
    'Payment Type'
    __name__ = 'account.payment.type'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code')
    active = fields.Boolean('Active')
    company = fields.Many2One('company.company', 'Company', required=True,
        select=True, readonly=True, domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', 0)),
            ])
    note = fields.Text('Description', translate=True,
        help=('Description of the payment type that will be shown in '
            'descriptions'))
    kind = fields.Selection([
        ('payable', 'Payable'),
        ('receivable', 'Receivable'),
        ], 'Kind of payment type', help='The kind of payment type.', required=True)

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    def get_rec_name(self, name):
        if self.code:
            return '[' + self.code + '] ' + self.name
        else:
            return self.name
