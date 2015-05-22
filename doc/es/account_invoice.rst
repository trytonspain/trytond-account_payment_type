#:before:account_invoice/account_invoice:section:cancelar#

.. inheritref:: account_payment_type/account_invoice:section:payment_type

Tipos de pago
-------------

Los tipos de pago le permiten a una factura especificar el sistema de pago que
debe usar el cliente para pagar y relacionar con el tercero el tipo de pago por defecto. 

Cuando se crea una factura y selecciona el tercero, se autocompleta el tipo de pago según
el tipo del pago del tercero. Si lo desea en la factura, el tipo de pago lo puede cambiar por
otro tipo de pago que no sea el pago por defecto del tercero.

A |menu_account_payment_type_form| podrá añadir los tipos de pago y especificar si son de cobro o de pago.
Se recomienda en los tipos de pago "manuales" añadir detalles en la descripción (por ejemplo, un pago
del tipo Transferencia bancaria, añadir en la descripción la cuenta corriente para hacer el pago).

Si usais la opción de duplicar un tipo de pago, recordad de cambiar el nombre y la descripción en
todos los idiomas.

.. |menu_account_payment_type_form| tryref:: account_payment_type.menu_account_payment_type_form/complete_name
