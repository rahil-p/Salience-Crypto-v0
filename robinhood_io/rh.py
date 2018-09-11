#built on top of Jamonek/Robinhood (crypto API support added)

import warnings
import requests
import getpass
import uuid

from robinhood_io import endpoints, exceptions
from robinhood_io.pairs import PAIRS
import config

class Robinhood:

    def __init__(self):

        self.headers = {'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                        'X-Robinhood-API-Version': '1.0.0',
                        'Connection': 'keep-alive',
                        'User-Agent': 'Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)'}

        self._username = config.rh_username
        self._password = config.rh_password
        self.auth_method = self.login

        self.api_session = requests.session()
        self.api_session.headers = self.headers

        self.nummus_session = requests.session()
        self.nummus_session.headers = self.headers

        #check auth_token and headers compatibility for nummus

    def login_required(function):                       #decorator function
        def wrapper(self, *args, **kwargs):
            if 'Authorization' not in self.headers:
                self.auth_method()
            return function(self, *args, **kwargs)
        return wrapper

    def login(self):
        payload = {'username': self._username,
                   'password': self._password}

        try:
            res = self.api_session.post(endpoints.api_login(), data=payload, timeout=15)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log in: ' + repr(err_msg))
            raise exceptions.LoginFailed()

        if 'token' in data.keys():
            self.auth_token = data['token']
            self.headers['Authorization'] = 'Token ' + self.auth_token

        return

    def logout(self):
        try:
            req = self.api_session.post(endpoints.api_logout(), timeout=15)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log out: ' + repr(err_msg))
            raise exceptions.LogoutFailed()

        self.headers['Authorization'] = None
        self.auth_token = None

        return

    #-----

    def get_power(self):
        try:
            res = self.api_session.get(endpoints.api_accounts(), timeout=10)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.HTTPError:
            raise exceptions.AccessFailed()

        return data['results'][0]['margin_balances']['unallocated_margin_cash']

    #-----

    def order_crypto(self, symbol, order_type, order_side, price, quantity):
        pair_id = PAIRS[symbol]

        body = {'side': order_side,
                'currency_pair_id': pair_id,
                'type': order_type,
                'price': price,
                'quantity': quantity,
                'time_in_force': 'gtc',
                'uuid': str(uuid.uuid4)}

        try:
            res = self.nummus_session.post(endpoints.nummus_orders(), timeout=15)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to complete transaction: ' + repr(err_msg))
            return False

        return data
