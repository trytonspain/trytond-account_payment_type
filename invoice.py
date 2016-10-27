# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from collections import defaultdict
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, Not
from trytond.transaction import Transaction
from trytond.modules.account_payment_type.payment_type import KINDS

__all__ = ['Invoice']
ZERO = Decimal('0.0')


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'
    payment_type_kind = fields.Function(fields.Selection(KINDS,
            'Kind of payment type',
            states={
                'invisible': True,
                },
            ),
        'on_change_with_payment_type_kind')
    payment_type = fields.Many2One('account.payment.type', 'Payment Type',
        domain=[
            ('kind', 'in', ['both', Eval('payment_type_kind')]),
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
        return 'receivable' if self.type == 'out' else 'payable'

    @fields.depends('party', 'company', 'type', 'untaxed_amount', 'lines',
        'payment_type', methods=['payment_type_kind'])
    def on_change_with_payment_type(self, name=None):
        kind = self.on_change_with_payment_type_kind()
        if (self.payment_type and self.payment_type.kind in ['both', kind]):
            return self.payment_type.id
        if not self.untaxed_amount:
            return None
        for party in [
                self.party,
                self.company.party if self.company else None]:
            if not party:
                continue
            if self.type == 'out':
                if self.untaxed_amount >= ZERO:
                    name = 'customer_payment_type'
                else:
                    name = 'supplier_payment_type'
            elif self.type == 'in':
                if self.untaxed_amount >= ZERO:
                    name = 'supplier_payment_type'
                else:
                    name = 'customer_payment_type'
            payment_type = getattr(party, name)
            if payment_type:
                return payment_type.id
        return None

    @classmethod
    def post(cls, invoices):
        pool = Pool()
        Date = pool.get('ir.date')
        Payment = pool.get('account.payment')
        PayLine = pool.get('account.move.line.pay', type='wizard')
        super(Invoice, cls).post(invoices)
        lines_to_pay = defaultdict(list)
        for invoice in invoices:
            if (invoice.payment_type
                    and invoice.payment_type.payment_journal):
                for line in invoice.lines_to_pay:
                    key = (invoice.payment_type, line.maturity_date)
                    lines_to_pay[key].append(line.id)

        to_approve = []
        for key, lines in lines_to_pay.iteritems():
            payment_type, date = key
            session_id, _, _ = PayLine.create()
            payline = PayLine(session_id)
            payline.ask_journal.journal = payment_type.payment_journal
            payline.ask_journal.date = date or Date.today()
            with Transaction().set_context(active_ids=lines):
                action, data = payline.do_pay(None)
            if payment_type.approve_payments:
                to_approve.extend(data['res_id'])
            PayLine.delete(session_id)
        if to_approve:
            Payment.approve(Payment.browse(to_approve))
