# This file is part of account_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Bool
from trytond.pool import Pool
from trytond import backend

__all__ = ['PaymentType']

KINDS = [
    ('both', 'Both'),
    ('payable', 'Payable'),
    ('receivable', 'Receivable'),
    ]


class PaymentType(ModelSQL, ModelView):
    'Payment Type'
    __name__ = 'account.payment.type'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active')
    note = fields.Text('Description', translate=True,
        help=('Description of the payment type that will be shown in '
            'descriptions'))
    kind = fields.Selection(KINDS, 'Kind', required=True)
    journals = fields.One2Many('account.payment.journal', 'payment_type',
        'Journals')
    payment_journal = fields.Many2One('account.payment.journal',
        'Default Journal',
        domain=[
            ('payment_type', '=', Eval('id')),
            ],
        states={
            'invisible': ~Bool(Eval('journals', [])),
            },
        depends=['id', 'journals'],
        help=('The payment journal for creating payments when the invoices '
            'are posted. A payment for each maturity date will be created.'))
    approve_payments = fields.Boolean('Aprove Payments?',
        states={
            'invisible': ~Bool(Eval('payment_journal', 0)),
            },
        depends=['payment_journal'],
        help='If marked, payments will be approved after creation')

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        table = TableHandler(cls, module_name)

        super(PaymentType, cls).__register__(module_name)

        # Migration from 4.2: drop required on company
        table.not_null_action('company', action='remove')

    @classmethod
    def __setup__(cls):
        super(PaymentType, cls).__setup__()
        cls._check_modify_fields = set(['kind'])
        cls._check_modify_related_models = set([
                ('account.invoice', 'payment_type'),
                ])
        cls._error_messages.update({
                'modifiy_with_related_model': ('It is not possible to modify '
                    'the field "%(field)s" as the payment type "%(type)s" is '
                    'used on %(model)s "%(name)s"'),
                })

    @staticmethod
    def default_active():
        return True

    @classmethod
    def default_kind(cls):
        return 'both'

    @fields.depends('payment_journal', 'approve_payments')
    def on_change_payment_journal(self):
        if not self.payment_journal:
            self.approve_payments = False

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        args = []
        for payment_types, values in zip(actions, actions):
            keys = set(values.keys()) & cls._check_modify_fields
            if keys:
                cls.check_modify_fields(payment_types, keys)
            args.extend((payment_types, values))
        super(PaymentType, cls).write(*args)

    @classmethod
    def copy(cls, records, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default.setdefault('journals')
        default.setdefault('payment_journal')
        return super(PaymentType, cls).copy(records, default=default)

    @classmethod
    def check_modify_fields(cls, payment_types, fields):
        pool = Pool()
        IrModel = pool.get('ir.model')
        Field = pool.get('ir.model.field')
        payment_ids = [p.id for p in payment_types]
        for model_name, field_name in cls._check_modify_related_models:
            Model = pool.get(model_name)
            records = Model.search([(field_name, 'in', payment_ids)], limit=1)
            if records:
                record, = records
                model, = IrModel.search([('model', '=', model_name)])
                field, = Field.search([
                        ('model.model', '=', cls.__name__),
                        ('name', 'in', list(fields)),
                        ], limit=1)
                # Use payment from record to be coherent in error message
                payment_type = getattr(record, field_name)
                error_args = {
                    'name': record.rec_name,
                    'model': model.name,
                    'type': payment_type.rec_name,
                    'field': field.field_description,
                    }
                cls.raise_user_error('modifiy_with_related_model', error_args)
