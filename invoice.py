# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Bool, Eval, Not

__all__ = ['Invoice']
ZERO = Decimal('0.0')


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'
    payment_type_kind = fields.Function(fields.Selection([
            ('payable', 'Payable'),
            ('receivable', 'Receivable'),
            ], 'Kind of payment type',
            states={
                'invisible': True,
                },
            ),
        'on_change_with_payment_type_kind')
    payment_type = fields.Many2One('account.payment.type', 'Payment Type',
        domain=[
            ('kind', '=', Eval('payment_type_kind')),
            ],
        states={
            'readonly': Not(Bool(Eval('state').in_(['draft', 'validated']))),
            },
        depends=['payment_type_kind', 'state'])

    @fields.depends('type', 'untaxed_amount', 'lines')
    def on_change_with_payment_type_kind(self, name=None):
        if self.untaxed_amount:
            if self.type == 'out':
                if self.untaxed_amount >= ZERO:
                    return 'receivable'
                else:
                    return 'payable'
            elif self.type == 'in':
                if self.untaxed_amount >= ZERO:
                    return 'payable'
                else:
                    return 'receivable'

    @fields.depends('party', 'company', 'type', 'untaxed_amount', 'lines',
        'payment_type', methods=['payment_type_kind'])
    def on_change_with_payment_type(self, name=None):
        kind = self.on_change_with_payment_type_kind()
        if (self.payment_type and self.payment_type.kind == kind):
            return self.payment_type.id
        if not self.untaxed_amount:
            return None
        if self.party:
            if self.type == 'out':
                if (self.untaxed_amount >= ZERO
                        and self.party.customer_payment_type):
                    return self.party.customer_payment_type.id
                elif (self.untaxed_amount < ZERO
                        and self.party.supplier_payment_type):
                    return self.party.supplier_payment_type.id
            elif self.type == 'in':
                if (self.untaxed_amount >= ZERO
                        and self.party.supplier_payment_type):
                    return self.party.supplier_payment_type.id
                elif (self.untaxed_amount < ZERO
                        and self.party.customer_payment_type):
                    return self.party.customer_payment_type.id

        if self.company:
            if self.type == 'out':
                if (self.untaxed_amount >= ZERO
                        and self.company.party.customer_payment_type):
                    return self.company.party.customer_payment_type.id
                elif (self.untaxed_amount < ZERO
                        and self.company.party.supplier_payment_type):
                    return self.company.party.supplier_payment_type.id
            elif self.type == 'in':
                if (self.untaxed_amount >= ZERO
                        and self.company.party.supplier_payment_type):
                    return self.company.party.supplier_payment_type.id
                elif (self.untaxed_amount < ZERO
                        and self.company.party.customer_payment_type):
                    return self.company.party.customer_payment_type.id
        return None

    def _get_move_line(self, date, amount):
        res = super(Invoice, self)._get_move_line(date, amount)
        if self.payment_type:
            res['payment_type'] = self.payment_type
        return res
