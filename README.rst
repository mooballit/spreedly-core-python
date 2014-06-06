============================
Spreedly Core Python Library
============================

Spreedly Core Python Library is a Python wrapper for the Spreedly Core API.

License
-------

All material is Copyright Mooball IT

All code is licensed under the ZPL Licence (see LICENSE.txt)

Requirements
------------

* Active Spreedly Core Account (https://spreedlycore.com)
* Python >= 2.6

Changes
------------
Version 0.4

* Removed Transaction.add() method and added explicit Transaction.purchase() for Purchase transaction types.
* PaymentGateway.transaction() will work as before and execute a Purchase transaction by default but has an optional parameter, transaction_type, to still use this wrapper method for an authorize (and subsequent capture) will need to pass transaction_type = 'authorize'.

Version 0.3

* Added from_dict method to PaymentGateway to pop 'gateway' tag, now resembles old functionality. Variable 'xml' in RequestFailed uses Dictionary Tree instead of ElementTree, added 'errors_field' for easy access of 'errors' in 'payment_method'.

Version 0.2

* Data Variable in APIObject now uses moesian's custom Dictionary Tree instead of ElementTree. Fixes bug involving the 'errors' field within 'payment_method', where ElementTree would not recurse far enough. Thanks moesian!

Contributions
-------------

* moesian (https://github.com/moesian)

Usage Examples
--------------

First create an APIConnection with login and secret

>>> api = APIConnection( 'LOGIN', 'SECRET' )

Get the first payment gateway and payment method

>>> pg = api.gateways()[0]
>>> pm = api.methods()[0]

Perform a Purchase transaction using the gateway and payment method.

>>> pg.transaction( pm, 100, 'USD')

Or

>>> t = Transaction.purchase(api, pg, pm, 100, 'USD')

Create a new gateway and payment method and retain the payment method for later.

>>> pg = PaymentGateway.add( api, 'test' )
>>> pm = PaymentMethod.add( api, { 'first_name': 'Test', 'last_name': 'Testington', 'number': '5555555555554444', 'verification_value': '666', 'month': '12', 'year': '2012' } )
>>> pm.retain()

Do another transaction via authorize (allocate funds but dont do transaction) and capture (do the transaction) using the new details.

>>> t = pg.transaction(pm, 1000, 'AUD', transaction_type = 'authorize')
>>> t.capture()

Or

>>> t = Transaction.authorize( api, pg, pm, 1000, 'AUD' )
>>> t.capture()

