# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction
from trytond.i18n import gettext
from trytond.exceptions import UserError
from trytond.modules.account_payment_type.payment_type import KINDS

__all__ = ['Move', 'Line']


class Move(metaclass=PoolMeta):
    __name__ = 'account.move'

    def cancel(self, default=None):
        with Transaction().set_context(cancel_move=True):
            return super(Move, self).cancel(default=default)


class Line(metaclass=PoolMeta):
    __name__ = 'account.move.line'

    account_kind = fields.Function(fields.Selection([
            ('', ''),
            ('payable', 'Payable'),
            ('receivable', 'Receivable')
            ], 'Kind'),
        'on_change_with_account_kind', searcher='search_account_kind')
    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', domain=[
            ('kind', 'in', ['both', Eval('account_kind')]),
            ], depends=['account_kind', 'reconciliation'],
        states={
                'readonly': Bool(Eval('reconciliation')),
                'invisible': ~Eval('account_kind', '').in_(
                    ['payable', 'receivable']),
            })
    payment_type_kind = fields.Function(fields.Selection(KINDS,
            'Kind of payment type',
            states={
                'invisible': True,
                },
            ),
        'on_change_with_payment_type_kind')

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()
        if hasattr(cls, '_check_modify_exclude'):
            cls._check_modify_exclude.add('payment_type')

    @classmethod
    def validate(cls, lines):
        super(Line, cls).validate(lines)
        for line in lines:
            line.check_account_payment_type()

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        if (Transaction().context.get('cancel_move')
                and 'payment_type' not in default):
            default['payment_type'] = None
        return super(Line, cls).copy(lines, default)

    def check_account_payment_type(self):
        if (self.payment_type
                and self.account.type.payable == False
                and self.account.type.receivable == False ):
            raise UserError(gettext(
                'account_payment_type.invalid_account_payment_type',
                payment=self.rec_name))

    @fields.depends('account', 'credit', 'debit')
    def on_change_with_account_kind(self, name=None):
        if self.account and (self.account.type.payable or
                self.account.type.receivable):
            if self.credit > 0 or self.debit < 0:
                return 'payable'
            elif self.debit > 0 or self.credit < 0:
                return 'receivable'
            return 'receivable' if self.account.type.receivable else 'payable'
        return ''

    @classmethod
    def search_account_kind(cls, name, clause):
        value = clause[2]
        return [('account.type.%s'%value,) + tuple(clause[1], True)]

    @fields.depends('account')
    def on_change_account(self):
        super(Line, self).on_change_account()
        if self.account and (self.account.type.payable == True
                or self.account.type.receivable == True):
            self.account_kind = ('payable' if self.account.type.payable
                else 'receivable')

    @fields.depends('payment_type')
    def on_change_with_payment_type_kind(self, name=None):
        if self.payment_type:
            return self.payment_type.kind
