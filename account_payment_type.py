#This file is part of account_payment_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pyson import Eval, If

__all__ = ['AccountPaymentType']

class AccountPaymentType(ModelSQL, ModelView):
    'Account Payment Type'
    __name__ = 'account.payment.type'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active')
    company = fields.Many2One('company.company', 'Company', required=True,
        select=True, readonly=True)
    note = fields.Text('Description', translate=True,
        help='Description of the payment type that will be shown in descriptions')

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_company():
        return Transaction().context.get('company')
