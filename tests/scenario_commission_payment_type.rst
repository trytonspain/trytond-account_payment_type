================================
Commission Payment Type Scenario
================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, set_tax_code
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install commission::

    >>> Module = Model.get('ir.module')
    >>> for module in Module.find([
    ...         ('name', 'in', ['commission', 'account_payment_type']),
    ...         ]):
    ...     module.click('install')
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create commission product::

    >>> Uom = Model.get('product.uom')
    >>> Template = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = Uom.find([('name', '=', 'Unit')])
    >>> commission_product = Product()
    >>> template = Template()
    >>> template.name = 'Commission'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal(0)
    >>> template.cost_price = Decimal(0)
    >>> template.account_expense = accounts['expense']
    >>> template.account_revenue = accounts['revenue']
    >>> template.save()
    >>> commission_product.template = template
    >>> commission_product.save()

Create commission plan::

    >>> Plan = Model.get('commission.plan')
    >>> plan = Plan(name='Plan')
    >>> plan.commission_product = commission_product
    >>> plan.commission_method = 'payment'
    >>> line = plan.lines.new()
    >>> line.formula = 'amount * 0.1'
    >>> plan.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create payment type::

    >>> PaymentType = Model.get('account.payment.type')
    >>> receivable = PaymentType(name='Receivable', kind='receivable')
    >>> receivable.save()
    >>> payable = PaymentType(name='Payable', kind='payable')
    >>> payable.save()

Create agent::

    >>> Agent = Model.get('commission.agent')
    >>> agent_party = Party(name='Agent')
    >>> agent_party.supplier_payment_term = payment_term
    >>> agent_party.customer_payment_type = receivable
    >>> agent_party.supplier_payment_type = payable
    >>> agent_party.save()
    >>> agent = Agent(party=agent_party)
    >>> agent.type_ = 'agent'
    >>> agent.plan = plan
    >>> agent.currency = company.currency
    >>> agent.save()

Create principal::

    >>> principal_party = Party(name='Principal')
    >>> principal_party.customer_payment_term = payment_term
    >>> principal_party.customer_payment_type = receivable
    >>> principal_party.supplier_payment_type = payable
    >>> principal_party.save()
    >>> principal = Agent(party=principal_party)
    >>> principal.type_ = 'principal'
    >>> principal.plan = plan
    >>> principal.currency = company.currency
    >>> principal.save()

Create commissions::

    >>> Commission = Model.get('commission')

    >>> commission_out = Commission()
    >>> commission_out.agent = principal
    >>> commission_out.product = commission_product
    >>> commission_out.amount = Decimal(10)
    >>> commission_out.save()

    >>> commission_in = Commission()
    >>> commission_in.agent = agent
    >>> commission_in.product = commission_product
    >>> commission_in.amount = Decimal(10)
    >>> commission_in.save()

Create invoices::

    >>> create_invoice = Wizard('commission.create_invoice')
    >>> create_invoice.form.from_ = None
    >>> create_invoice.form.to = None
    >>> create_invoice.execute('create_')

    >>> commission_out.reload()
    >>> commission_out.invoice_line.invoice.type == 'out'
    True
    >>> commission_out.invoice_line.invoice.payment_type == receivable
    True

    >>> commission_in.reload()
    >>> commission_in.invoice_line.invoice.type == 'in'
    True
    >>> commission_in.invoice_line.invoice.payment_type == payable
    True

