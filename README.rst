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

Usage Examples
--------------

First create an APIConnection with login and secret

>>> api = APIConnection( 'LOGIN', 'SECRET' )

Get the first payment gateway and payment method

>>> pg = api.gateways()[0]
>>> pm = api.methods()[0]

Raise a transaction using the gateway and payment method.

>>> pg.transaction( pm, 100, 'USD' )

Create a new gateway and payment method and retain the payment method for later.

>>> pg = PaymentGateway.add( api, 'test' )
>>> pm = PaymentMethod.add( api, { 'first_name': 'Test', 'last_name': 'Testington', 'number': '5555555555554444', 'verification_value': '666', 'month': '12', 'year': '2012' } )
>>> pm.retain()

Do another transaction via authorize (allocate funds but dont do transaction) and capture (do the transaction) using the new details.

>>> t = Transaction.authorize( api, pg, pm, 1000, 'AUD' )
>>> t.capture()

