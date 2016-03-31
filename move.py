# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction

__all__ = ['Move', 'Line']
__metaclass__ = PoolMeta


class Move:
    __name__ = 'account.move'

    def cancel(self, default=None):
        with Transaction().set_context(cancel_move=True):
            return super(Move, self).cancel(default=default)


class Line:
    __name__ = 'account.move.line'

    account_kind = fields.Function(fields.Selection([
            ('', ''),
            ('payable', 'Payable'),
            ('receivable', 'Receivable')
            ], 'Kind'),
        'on_change_with_account_kind', searcher='search_account_kind')
    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', domain=[
            ('kind', '=', Eval('account_kind')),
            ], depends=['account_kind', 'reconciliation'],
        states={
                'readonly': Bool(Eval('reconciliation')),
                'invisible': ~Eval('account_kind', '').in_(
                    ['payable', 'receivable']),
            })

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()
        if hasattr(cls, '_check_modify_exclude'):
            cls._check_modify_exclude.add('payment_type')
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

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        if (Transaction().context.get('cancel_move') and not 'payment_type' in
                default):
            default['payment_type'] = None
        return super(Line, cls).copy(lines, default)

    def check_account_payment_type(self):
        if (self.payment_type
                and self.account.kind not in ('payable', 'receivable')):
            self.raise_user_error('invalid_account_payment_type',
                (self.rec_name,))

    @fields.depends('account', 'credit', 'debit')
    def on_change_with_account_kind(self, name=None):
        if self.account and self.account.kind in ('payable', 'receivable'):
            if self.credit > 0 or self.debit < 0:
                return 'payable'
            elif self.debit > 0 or self.credit < 0:
                return 'receivable'
            return self.account.kind
        return ''

    @classmethod
    def search_account_kind(cls, name, clause):
        return [('account.kind',) + tuple(clause[1:])]

    @fields.depends('account')
    def on_change_account(self):
        super(Line, self).on_change_account()
        if self.account and self.account.kind in ('payable', 'receivable'):
            self.account_kind = self.account.kind
