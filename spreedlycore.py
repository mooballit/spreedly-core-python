# All material is Copyright Mooball IT
# All code is licensed under the ZPL Licence (see LICENSE.txt)

import urllib2, urlparse, datetime, base64
from xml.etree import ElementTree
from xmlutils import xml_to_dict, dict_to_xml


class APIConnection( object ):
    def __init__( self, login, secret, base_url = None ):
        self.base_url = base_url or 'https://spreedlycore.com/v1/'
        self.login = login
        self.secret = secret

    def gateways( self ):
        '''Returns a list of available gateways'''
        xml = APIRequest( self, 'gateways.xml' ).xml()
        
        if xml.tag == 'gateways':
            ret = []
            for elem in xml:
                o = PaymentGateway.__new__( PaymentGateway )
                o.from_dict( xml_to_dict( elem ) )
                o.api = self
                ret.append( o )
            
            return ret

        return []
    
    def methods( self ):
        '''Returns a list of available gateways'''
        xml = APIRequest( self, 'payment_methods.xml' ).xml()
        
        if xml.tag == 'payment_methods':
            ret = []
            for elem in xml:
                o = PaymentMethod.__new__( PaymentMethod )
                o.from_dict( xml_to_dict( elem ) )
                o.api = self
                ret.append( o )
            
            return ret

        return []
    
    def transactions( self, since = None ):
        ''' Returns a list of 20 transactions.
            Passing a transaction token in the since parameter will return
            20 transactions that occured after the supplied transaction token.
        '''
        url = 'transactions.xml'
        if since:
            url += '?since_token=%s' % since
        
        xml = APIRequest( self, url ).xml()
        
        if xml.tag == 'transactions':
            ret = []
            for elem in xml:
                o = Transaction.__new__( Transaction )
                o.from_dict( xml_to_dict( elem ) )
                o.api = self
                ret.append( o )
            
            return ret

        return []
    
    def gateway_types( self ):
        '''
        Returns a list of dictionaries that represent the available payment gateway
        types and the parameters they require to function.
        Each gateway type dictionary has a list of modes that correspond to
        different authentication modes that require a different set of parameters.
        And each of the modes have a list of fields which are the parameters needed to use the gateway.
        Appart from name and label each field also has attributes indicating
        whether the field's data is safe to display as plain text (the safe attribute)
        and whether a text box is needed to provide data to the it (the long attribute).
        This data can be used to easily generate forms to collect the correct
        authentication data for a client's payment gateway of choice.
        '''

        xml = APIRequest( self, 'gateways.xml', 'OPTIONS' ).xml()
        
        gws = []
        
        for elem in xml:
            gw = {}
            
            gw['type'] = elem.find( 'gateway_type' ).text
            gw['name'] = elem.find( 'name' ).text
            
            gw['modes'] = []
            
            for m_elem in elem.find( 'auth_modes' ) or []:
                mode = {}
                
                mode['type'] = m_elem.find( 'auth_mode_type' ).text
                mode['name'] = m_elem.find( 'name' ).text
                
                mode['fields'] = []
                
                for f_elem in m_elem.find( 'credentials' ):
                    field = {}
                    
                    field['name'] = f_elem.find( 'name' ).text
                    field['label'] = f_elem.find( 'name' ).text

                    if f_elem.find( 'safe' ) != None:
                        field['safe'] = f_elem.find( 'safe' ).text == 'true'
                    else:
                        field['safe'] = False

                    if f_elem.find( 'large' ) != None:
                        field['large'] = f_elem.find( 'large' ).text == 'true'
                    else:
                        field['large'] = False
                    
                    mode['fields'].append( field )
                
                gw['modes'].append( mode )
            
            gws.append( gw )
        
        return gws
        
        


class APIRequest( object ):
    class RequestFailed( Exception ):
        '''
            Indicates that the Request failed.
            Any returned xml data will be stored in the xml attribute and any
            error messages passed back will be stored in the errors attribute
        '''
        def __init__( self, data ):
            self.xml = ElementTree.fromstring( data )
            
            self.errors = []
            if self.xml.tag == 'errors':
                for elem in self.xml:
                    e = {}
                    e['text'] = elem.text
                    for k,v in elem.items():
                        e[k] = v
                    
                    self.errors.append( e )
            elif self.xml.tag == 'transaction':
                elem = self.xml.find( 'message' )
                e = {}
                e['text'] = elem.text
                for k,v in elem.items():
                    e[k] = v
                
                self.errors.append( e )
            elif self.xml.find( 'errors', None ):
                for elem in self.xml.find( 'errors' ):
                    e = {}
                    e['text'] = elem.text
                    for k,v in elem.items():
                        e[k] = v
                    
                    self.errors.append( e )
    
    def __init__( self, api, url, method = 'GET', data = None ):
        self.api = api
        self.url = url
        self.method = method
        self.data = data
        
    def do( self ):
        ''' Does the API Request and returns data as string '''
        req_url = urlparse.urljoin( self.api.base_url, self.url )
        
        req = urllib2.Request( url = req_url )

        req.add_data( self.data )
        req.add_header( 'Content-Type', 'application/xml' )

        # Deal with authentication ( Doing it the normal python way does not work with this API! )
        req.add_header( 'Authorization', 'Basic %s' % ( base64.b64encode( '%s:%s' % ( self.api.login, self.api.secret ) ) ) )
        
        # Set request method GET/POST/PUT/etc..
        req.get_method = lambda: self.method
        
        try:
            con = urllib2.urlopen( req )

            return con.read()
        except urllib2.HTTPError, e:
            if e.code == 422:
                # Assume request failed but data should be returned anyway
                raise APIRequest.RequestFailed( e.fp.read() )
            
            raise
    
    def xml( self ):
        ''' Does the API Request and returns data as an eTree '''
        return ElementTree.fromstring( self.do() )
    
    def to_object( self, cls, target = None ):
        '''
            Stores the returned data against an API Object.
            If target is supplied the data will be stored on the supplied object instead of a new one.
            The handlers parameter will be passed on to the xml_to_dict function.
        '''
        d = xml_to_dict( self.xml())
        
        if target:
            o = target
        else:
            o = cls.__new__( cls )
        
        o.api = self.api
        o.from_dict( d )
        return o
        

class APIObject( object ):
    '''
        Base object for each of the object types defined in the API.
        The init method only takes the api and the objects token as this is usually all that is required to do requests.
        Creating a new object is done using the add class-method instead.
    '''
    def __init__( self, api, token ):
        self.api = api
        self.token = token
    
    @classmethod
    def add( cls ):
        pass
    
    def from_dict( self, data ):
        '''
            Used to update the objects attributes with data from the data dictionary.
            This method can be overridden to handle specific data differently. See Transaction for example.
        '''
        self.token = data.pop( 'token', None )
        self.data = data
    
    def __repr__( self ):
        return '<%s token=%s>' % ( self.__class__.__name__, self.token )
    
class PaymentGateway( APIObject ):
    @classmethod
    def add( cls, api, type, **params ):
        '''
            Creates a new Payment Gateway.
            type is the type name of the payment gateway to be created.
            Any extra parameters required by the gateway type should be passed as keyword arguments.
            Run api.gateway_types() to get a list of supported gateway types and what parameters they require.
        '''

        data = { 'gateway': { 'gateway_type': type } }
        data['gateway'].update( params )

        data = dict_to_xml( data )
        
        ret = APIRequest( api, 'gateways.xml', data = data ).to_object( PaymentGateway )
        return ret
    
    def load( self ):
        APIRequest( self.api, 'gateways/%s.xml' % self.token, data = '' ).to_object( PaymentGateway, target = self )

        return self
    
    def transaction( self, pm, amount, currency ):
        '''
            Shortcut method to do a transaction using this gateway
            pm is a payment method object
        '''
        
        return Transaction.add( self.api, self, pm, amount, currency )
    
    def from_dict( self, data ):
            if 'gateway' in data:
                data = data.pop( 'gateway' )
            super( PaymentGateway, self ).from_dict( data )

class PaymentMethod( APIObject ):
    @classmethod
    def add( cls, api, credit_card ):
        '''
        Creates a new Payment Method.
        
        WARNING: Using this method to create payment methods should only be used
        if you are unable to use the standard method outlined in: https://spreedlycore.com/manual/quickstart
        
        The standard method is safer because you do not have to touch the credit
        card data as it is sent straight to spreedly core via the form.
        credit_card is a dictionary with credit card details with the following keys:
        first_name, last_name, number, verification_value, month, year
        Where number is the credit card number and month and year are for
        the expiration date. The year is expressed using 4 digits (ie 2012)
        '''
        d = dict_to_xml( { 'credit_card': credit_card } )
       
        req = APIRequest( api, 'payment_methods.xml', 'POST', data = d )

        o = PaymentMethod.__new__( cls )
        o.from_dict( xml_to_dict( req.xml().find( 'payment_method' ) ) )

        return o

    def retain( self ):
        '''
            This will store the Payment Method for later use. If a payment method is not retained, you will only be able to use it once.
        '''
        req = APIRequest( self.api, 'payment_methods/%s/retain.xml' % self.token, 'PUT', '' )
        self.from_dict( xml_to_dict( req.xml().find( 'payment_method' ) ) )

        return self

    def redact( self ):
        '''
            This will redact a previously retained payment method making it unavailable for any future transactions.
        '''
        req = APIRequest( self.api, 'payment_methods/%s/redact.xml' % self.token, 'PUT', '' )
        self.from_dict( xml_to_dict( req.xml().find( 'payment_method' ) ) )

        return self
        

    def load( self ):
        APIRequest( self.api, 'payment_methods/%s.xml' % self.token, data = '' ).to_object( PaymentMethod, target = self )

        return self
    
    def update( self, **params ):
        '''
            This will update any non-sensitive attributes.
            Attempting to change things such as the card number will cause an error.
        '''
        data = dict_to_xml( { 'payment_method': params } )
        
        APIRequest( self.api, 'payment_methods/%s.xml' % self.token, 'PUT', data ).to_object( PaymentMethod, target = self )

        return self

    def transactions( self, since = None ):
        '''
            Will return a list of 20 transactions done using the payment method.
            Passing a transaction token in the since attribute will return 20 transactions that occured after the supplied transaction token.
        '''
        url = 'payment_methods/%s/transactions.xml' % self.token
        if since:
            url += '?since_token=%s' % since
        
        xml = APIRequest( self.api, url ).xml()
        
        if xml.tag == 'transactions':
            ret = []
            for elem in xml:
                o = Transaction.__new__( Transaction )
                o.__dict__ = xml_to_dict( elem )
                o.api = self
                ret.append( o )
            
            return ret

        return []

    def from_dict( self, data ):
            if 'payment_method' in data:
                data = data.pop( 'payment_method' )
            super( PaymentMethod, self ).from_dict( data )
        
class Transaction( APIObject ):
    @classmethod
    def add( cls, api, pg, pm, amount, currency, order_id = None, ip = None ):
        '''
            Creates a new transaction
            pg is the payment gateway to use
            pm is the payment method to use
            order_id is optional and would be used to link a transaction to an order in your system
            ip is the ip address that initiated the transaction. This should be the ip of the user using your system.
        '''
        data = {
            'transaction': {
                'amount': amount,
                'currency_code': currency,
                'payment_method_token': pm.token
            }
        }
        if order_id:
            data['transaction']['order_id'] = order_id
        if ip:
            data['transaction']['ip'] = ip
        
        data = dict_to_xml( data )

        return APIRequest( api, 'gateways/%s/purchase.xml' % pg.token, 'POST', data ).to_object( Transaction )

    @classmethod
    def authorize( cls, api, pg, pm, amount, currency, order_id = None, ip = None ):
        '''
            Works just like the add method except no funds are actually transfered.
            Use capture method to make the actual transfer or void method to cancel it.
        '''
        data = {
            'transaction': {
                'amount': amount,
                'currency_code': currency,
                'payment_method_token': pm.token
            }
        }
        if order_id:
            data['transaction']['order_id'] = order_id
        if ip:
            data['transaction']['ip'] = ip

        data = dict_to_xml( data )
        
        return APIRequest( api, 'gateways/%s/authorize.xml' % pg.token, 'POST', data ).to_object( Transaction )
    
    def capture( self, amount = None, order_id = None, ip = None ):
        '''
            Does the actual transfer for a Transaction created with authorize
        '''
        if amount or order_id or ip:
            data = { 'transaction': { } }
            if amount:
                data['transaction']['amount'] = amount
            if order_id:
                data['transaction']['order_id'] = order_id
            if ip:
                data['transaction']['ip'] = ip
            data = dict_to_xml( data )
        else:
            data = ''

        return APIRequest( self.api, 'transactions/%s/capture.xml' % self.token, 'POST', data ).to_object( Transaction, target = self )
    
    def void( self, order_id = None, ip = None ):
        '''
            Cancels a Transaction created with authorize
        '''
        if order_id or ip:
            data = { 'transaction': { } }
            if order_id:
                data['transaction']['order_id'] = order_id
            if ip:
                data['transaction']['ip'] = ip
            data = dict_to_xml( data )
        else:
            data = ''
        return APIRequest( self.api, 'transactions/%s/void.xml' % self.token, 'POST', '' ).to_object( Transaction, target = self )
    
    def credit( self, amount = None, order_id = None, ip = None ):
        '''
            Cancels or refunds any Transaction created in the past.
        '''
        if amount or order_id or ip:
            data = { 'transaction': { } }
            if amount:
                data['transaction']['amount'] = amount
            if order_id:
                data['transaction']['order_id'] = order_id
            if ip:
                data['transaction']['ip'] = ip
            data = dict_to_xml( data )
        else:
            data = ''

        return APIRequest( self.api, 'transactions/%s/credit.xml' % self.token, 'POST', '' ).to_object( Transaction, target = self )
        
    def from_dict( self, data ):
        data = data.pop( 'transaction' )
        if 'payment_method' in data:
            self.payment_method = PaymentMethod.__new__( PaymentMethod )
            self.payment_method.api = self.api
            self.payment_method.from_dict( data.pop( 'payment_method' ) )
        super( Transaction, self ).from_dict( data )
