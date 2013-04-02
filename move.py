#This file is part of account_payment_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['Line']
__metaclass__ = PoolMeta

_STATES = {
    'readonly': Eval('state') != 'draft',
}
_DEPENDS = ['state']

class Line:
    __name__ = 'account.move.line'

    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', states=_STATES, depends=_DEPENDS)

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()
        cls._error_messages.update({
                'invalid_account_payment_type': ('Can not set Payment Type in '
                    'move line "%s" because account is not Payable nor '
                    'Receivable.'),
                })

    @classmethod
    def validate(cls, lines):
        super(Line, cls).validate(lines)
        for line in lines:
            line.check_account_payment_type()

    def check_account_payment_type(self):
        if (self.payment_type
                and self.account.kind not in ('payable', 'receivable')):
            self.raise_user_error('invalid_account_payment_type',
                (self.rec_name,))
