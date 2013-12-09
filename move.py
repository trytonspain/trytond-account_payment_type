# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Bool

__all__ = ['Line']
__metaclass__ = PoolMeta


class Line:
    __name__ = 'account.move.line'

    account_kind = fields.Function(fields.Selection([
            ('payable', 'Payable'),
            ('receivable', 'Receivable')
            ], 'Kind'),
        'get_account_kind', searcher='search_account_kind')
    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', domain=[
            # TODO: ('kind', '=', Eval('account_kind')),
            ], depends=['account_kind'],
        states={
                'readonly': Bool(Eval('reconciliation')),
            })

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()
        if hasattr(cls, '_check_modify_exclude'):
            cls._check_modify_exclude.append('payment_type')
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

    def get_account_kind(self, name):
        if self.account.kind in ('payable', 'receivable'):
            return self.account.kind
        return 'none'

    @classmethod
    def search_account_kind(cls, name, clause):
        return [('account.kind',) + tuple(clause[1:])]

    def on_change_account(self):
        changes = super(Line, self).on_change_account()
        if self.account and self.account.kind in ('payable', 'receivable'):
            changes['account_kind'] = self.account.kind
        else:
            changes['account_kind'] = None
        changes['payment_type'] = False
        return changes
