#!/usr/bin/env python
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, Gio
import os, sys, json, hmac, hashlib, time, requests, base64

class BitfinexError(Exception):
    pass

class BaseClient(object):
    """
    A base class for the API Client methods that handles interaction with
    the requests library.
    """
    #api_url = 'https://bf1.apiary-mock.com/'
    api_url = 'https://api.bitfinex.com/'
    exception_on_error = True

    def __init__(self, proxydict=None, *args, **kwargs):
        self.proxydict = proxydict

    def _get(self, *args, **kwargs):
        """
        Make a GET request.
        """
        return self._request(requests.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        """
        Make a POST request.
        """
        data = self._default_data()
        data.update(kwargs.get('data') or {})
        kwargs['data'] = data
        return self._request(requests.post, *args, **kwargs)

    def _default_data(self):
        """
        Default data for a POST request.
        """
        return {}

    def _request(self, func, url, *args, **kwargs):
        """
        Make a generic request, adding in any proxy defined by the instance.
        Raises a ``requests.HTTPError`` if the response status isn't 200, and
        raises a :class:`BitfinexError` if the response contains a json encoded
        error message.
        """
        return_json = kwargs.pop('return_json', False)
        url = self.api_url + url
        response = func(url, *args, **kwargs)

        if 'proxies' not in kwargs:
            kwargs['proxies'] = self.proxydict
            
        #print 'Response Code: ' + str(response.status_code) 
        #print 'Response Header: ' + str(response.headers)
        #print 'Response Content: '+ str(response.content)

        # Check for error, raising an exception if appropriate.
        response.raise_for_status()

        try:
            json_response = response.json()
        except ValueError:
            json_response = None
        if isinstance(json_response, dict):
            error = json_response.get('error')
            if error:
                raise BitfinexError(error)

        if return_json:
            if json_response is None:
                raise BitfinexError(
                    "Could not decode json for: " + response.text)
            return json_response

        return response


class Public(BaseClient):

    def ticker(self):
        """
        Returns dictionary. 
        
        mid (price): (bid + ask) / 2
        bid (price): Innermost bid.
        ask (price): Innermost ask.
        last_price (price) The price at which the last order executed.
        low (price): Lowest trade price of the last 24 hours
        high (price): Highest trade price of the last 24 hours
        volume (price): Trading volume of the last 24 hours
        timestamp (time) The timestamp at which this information was valid.
        
        """
        return self._get("v1/pubticker/btcusd", return_json=True)
    
    def get_last(self):
        """shortcut for last trade"""
        return float(self.ticker()['last_price'])
 

class Trading(Public):

    def __init__(self, key, secret, *args, **kwargs):
        """
        Stores the username, key, and secret which is used when making POST
        requests to Bitfinex.
        """
        super(Trading, self).__init__(
                 key=key, secret=secret, *args, **kwargs)
        self.key = key
        self.secret = secret

    def _get_nonce(self):
        """
        Get a unique nonce for the bitfinex API.
        This integer must always be increasing, so use the current unix time.
        Every time this variable is requested, it automatically increments to
        allow for more than one API request per second.
        This isn't a thread-safe function however, so you should only rely on a
        single thread if you have a high level of concurrent API requests in
        your application.
        """
        nonce = getattr(self, '_nonce', 0)
        if nonce:
            nonce += 1
        # If the unix time is greater though, use that instead (helps low
        # concurrency multi-threaded apps always call with the largest nonce).
        self._nonce = max(int(time.time()), nonce)
        return self._nonce

    def _default_data(self, *args, **kwargs):
        """
        Generate a one-time signature and other data required to send a secure
        POST request to the Bitfinex API.
        """
        data = {}
        nonce = self._get_nonce()
        data['nonce'] = str(nonce)
        data['request'] = args[0]
        return data

    def _post(self, *args, **kwargs):
        """
        Make a POST request.
        """
        data = kwargs.pop('data', {})
        data.update(self._default_data(*args, **kwargs))
        
        key = self.key
        secret = self.secret
        payload_json = json.dumps(data)
        payload = base64.b64encode(payload_json)
        sig = hmac.new(secret, payload, hashlib.sha384)
        sig = sig.hexdigest()

        headers = {
           'X-BFX-APIKEY' : key,
           'X-BFX-PAYLOAD' : payload,
           'X-BFX-SIGNATURE' : sig
           }
        kwargs['headers'] = headers
        
        #print("headers: " + json.dumps(headers))
        #print("sig: " + sig)
        #print("api_secret: " + secret)
        #print("api_key: " + key)
        #print("payload_json: " + payload_json)
        return self._request(requests.post, *args, **kwargs)

    def account_infos(self):
        """
        Returns dictionary::
        [{"fees":[{"pairs":"BTC","maker_fees":"0.1","taker_fees":"0.2"},
        {"pairs":"LTC","maker_fees":"0.0","taker_fees":"0.1"},
        {"pairs":"DRK","maker_fees":"0.0","taker_fees":"0.1"}]}]
        """
        return self._post("/v1/account_infos", return_json=True)
    
    def balances(self):
        """
        returns a list of balances
        A list of wallet balances:
        type (string): "trading", "deposit" or "exchange".
        currency (string): Currency 
        amount (decimal): How much balance of this currency in this wallet
        available (decimal): How much X there is in this wallet that 
        is available to trade.
        """
        return self._post("/v1/balances",return_json=True)
    
    def new_order(self, amount=0.01, price=1.11, side='buy', order_type='limit', symbol='btcusd'):
        """
        enters a new order onto the orderbook
        
        symbol (string): The name of the symbol (see `/symbols`).
        amount (decimal): Order size: how much to buy or sell.
        price (price): Price to buy or sell at. May omit if a market order.
        exchange (string): "bitfinex".
        side (string): Either "buy" or "sell".
        type (string): Either "market" / "limit" / "stop" / "trailing-stop" / "fill-or-kill" / "exchange market" / "exchange limit" / "exchange stop" / "exchange trailing-stop" / "exchange fill-or-kill". (type starting by "exchange " are exchange orders, others are margin trading orders) 
        is_hidden (bool) true if the order should be hidden. Default is false.
        Response
        
        order_id (int): A randomly generated ID for the order.
        and the information given by /order/status"""
        data = {'symbol': str(symbol),
                'amount': str(amount),
                'price': str(price),
                'exchange': 'bitfinex',
                'side':str(side),
                'type':order_type
                }
        return self._post("/v1/order/new", data=data, return_json=True)

    def orders(self):
        """
        Returns an array of the results of `/order/status` for all
        your live orders.
        """
        return self._post("/v1/orders", return_json=True)

    def cancel_order(self, order_id):
        """
        cancels order with order_id
        """
        data = {'order_id': str(order_id)}
        return self._post("/v1/order/cancel",data, return_json=True)
    
    def cancel_all_orders(self):
        """
        cancels all orders
        """
        req = self._post('/v1/order/cancel/all', return_json=False)
        if req.content == "All orders cancelled":
            return True
        else:
            return False
        
    def positions(self):
        """
        gets positions
        """
        return self._post("/v1/positions", return_json=True)


class bfxconsole(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self,
        application_id="org.ascension.bfxconsole",
        flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)
    
    def on_keyentry_change(self, entry, *data):
        """
        data contains a list with two entry widgets and the confirm button widget
        If both the entry widgets contain the right amount of characters, then
        the confirm button is set as sensitive and can be clicked.
        If both are confirmed, the keys are entered into the dconf settings database.
        """
        length1 = data[0].get_buffer().get_length()
        length2 = data[1].get_buffer().get_length()
        confirmbutton = data[2]
        login = data[3]
        if (length1 == 43) and (length2 == 43):
            apikey = data[0].get_buffer().get_text()
            apisecret = data[1].get_buffer().get_text()
            login.set_string ("apikey", apikey)
            login.set_string ("apisecret", apisecret)
            confirmbutton.set_sensitive (True)
        else: 
            confirmbutton.set_sensitive (False)
            
    def on_keyentry_confirm (self, button, *data):
        """
        When the user has entered two API credentials of the correct length
        check that the login is valid according to Bitfinex
        """
        window = data[0]
        entrygrid = data[1]
        login = data[2]
        apikey = data[2].get_string ("apikey")
        apisecret = data[2].get_string ("apisecret")
        window.remove (entrygrid)
        window.add (Gtk.Label (label="Checking Login Details..."))
        window.show_all ()
        self.test_login (window, login, apikey, apisecret)
        
    def test_login (self, window, login, apikey, apisecret):
        """
        Test whether the API key/secret are valid for Bitfinex.
        If they are invalid, change the window title to indicate this,
        and prompt the user to enter them again.
        This app saves all settings in the dconf database and any configuration
        changes are automatically saved so there is never a moment the user cannot
        simply close down the app. The rest of the data is saved on the Bitfinex
        servers and is reloaded when needed to display in this app.
        """
        success = False
        bfx_account = Trading (key=apikey, secret=apisecret)
        try:
            result = bfx_account.balances()
        except requests.exceptions.HTTPError:
            success = False
            window.set_title ("Invalid Login Credentials")
            login.set_string ("apikey", "")
            login.set_string ("apisecret", "")
            self.enter_keys (window, login, "", "")
            print ("bitfinex rejected credentials")
        else:
            window.set_title ("bfxconsole")
            child = window.get_child()
            if (child): 
                window.remove (child)
            window.add (Gtk.Label(label="starting console"))
            window.show_all ()
    
    def enter_keys (self, window, login, apikey, apisecret):
        """
        Change window content to prompt the user for API Key and Secret
        """
        apikeygrid = Gtk.Grid()
        child = window.get_child()
        if (child): 
            window.remove (child)
        apikeyinput = Gtk.Entry()
        apisecretinput = Gtk.Entry ()
        apiconfirmbutton = Gtk.Button (label="OK")
        apiconfirmbutton.set_sensitive (False)
        apikeygrid.attach (Gtk.Label (label="Please enter your Bitfinex API key and secret:"), 1, 1, 2, 1)
        apikeygrid.attach (Gtk.Label (label="API Key:"), 1, 2, 1, 1)
        apikeygrid.attach (Gtk.Label (label="API Secret:"), 1, 3, 1, 1)
        apikeygrid.attach (apikeyinput, 2, 2, 1, 1)
        apikeygrid.attach (apisecretinput, 2, 3, 1, 1)
        apikeygrid.attach (apiconfirmbutton, 1, 4, 2, 1)
        apikeyinput.connect ("changed", self.on_keyentry_change, 
        apikeyinput, apisecretinput, apiconfirmbutton, login)
        apisecretinput.connect ("changed", self.on_keyentry_change, 
        apikeyinput, apisecretinput, apiconfirmbutton, login)
        apiconfirmbutton.connect ("clicked", self.on_keyentry_confirm, window, apikeygrid, login)
        window.add (apikeygrid)
        window.show_all ()
        
    def on_activate(self, data=None):
        """
        Open application window, check for credentials, test login, then if successful,
        launch console interface.
        """
        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.add_window(window)
        
        window.set_title("bfxconsole")
        window.set_border_width(24)
        window.set_position(Gtk.WindowPosition.CENTER)
        
        login = Gio.Settings("org.ascension.bfxconsole")
        apikey = login.get_string("apikey")
        apisecret = login.get_string("apisecret")
        if (apikey == "") or (apisecret == ""):
            self.enter_keys (window, login, apikey, apisecret)
        else:
            self.test_login (window, login, apikey, apisecret)
        #window.show_all ()
        #print ("logged in")
    
        #public=Public()
        #print(public.ticker())
        #bfx_account = Trading (key='GBiBGM3b4ncW6HRbp5SYkrElWkUNj1PYyuVnHLnZwgk', 
        #    secret='HUaB2c0MkPlvtMUUYRIsThfPeC0qDaW5umLvACIdMVx')
        #print (bfx_account.positions ())
    

if __name__ == "__main__":
    app = bfxconsole()
    app.run(None)
