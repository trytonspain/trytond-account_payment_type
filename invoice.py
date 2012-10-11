#This file is part of account_payment_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['Invoice']
__metaclass__ = PoolMeta

_STATES = {
    'readonly': Eval('state') != 'draft',
}
_DEPENDS = ['state']

class Invoice:
    'Invoice'
    __name__ = 'account.invoice'

    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', states=_STATES, depends=_DEPENDS)

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
