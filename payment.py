# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Journal', 'Group']


class Journal:
    __metaclass__ = PoolMeta
    __name__ = 'account.payment.journal'

    payment_type = fields.Many2One('account.payment.type', 'Payment Type',
        required=True)


class Group:
    __metaclass__ = PoolMeta
    __name__ = 'account.payment.group'

    payment_type = fields.Function(fields.Many2One('account.payment.type',
            'Payment Type'),
        'on_change_with_payment_type')

    @fields.depends('journal')
    def on_change_with_payment_type(self, name=None):
        if self.journal and self.journal.payment_type:
            return self.journal.payment_type.id
