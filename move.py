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
