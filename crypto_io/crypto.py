import requests
import datetime
import pandas as pd

from crypto_io import exceptions
from crypto_io.info import CRYPTO_NAMES

class Crypto:

    def __init__(self, symbol):

        self.symbol = symbol
        self.name = CRYPTO_NAMES[symbol]

        self.url = 'https://min-api.cryptocompare.com/data/histominute' + \
                   '?fsym=' + symbol + \
                   '&tsym=USD' + \
                   '&aggregate=1'

        self.data = self.start_data()


    def start_data(self):

        try:
            res = requests.get(self.url + '&limit=2000', timeout=10)
            res.raise_for_status()
            data = res.json()['Data']
        except requests.exceptions.HTTPError:
            raise exceptions.ScrapeFailed()

        data = pd.DataFrame(data)
        data['time'] = [datetime.datetime.fromtimestamp(d) for d in data['time']]

        return data

    def update_data(self):

        try:
            res = requests.get(self.url + '&limit=10', timeout=10)
            res.raise_for_status()
            data = res.json()['Data']
        except requests.exceptions.HTTPError:
            raise exceptions.ScrapeFailed()

        tmp_data = pd.DataFrame(data)
        tmp_data['time'] = [datetime.datetime.fromtimestamp(d) for d in tmp_data['time']]

        tmp_new_data = self.data.merge(tmp_data, on=list(self.data), how='outer')
        tmp_new_data.drop_duplicates(subset=['time'], inplace=True, keep='last')
        tmp_new_data = tmp_new_data.sort_values('time').reset_index()

        self.data = tmp_new_data

        return
