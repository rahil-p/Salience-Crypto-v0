import requests
import datetime
import random

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.stattools import adfuller

from crypto_io import exceptions
from crypto_io.info import CRYPTO_NAMES, CRYPTO_COLORS, CRYPTO_IDS, CRYPTO_LEVERAGES

class Crypto:

    def __init__(self, symbol):

        self.symbol = symbol
        self.name = CRYPTO_NAMES[symbol]
        self.color = CRYPTO_COLORS[symbol] if symbol in CRYPTO_LEVERAGES else '#{:02x}{:02x}{:02x}'.format(random.randint(0,255),
                                                                                                           random.randint(0,255),
                                                                                                           random.randint(0,255))
        self.leverages = CRYPTO_LEVERAGES[symbol] if symbol in CRYPTO_LEVERAGES else None

        self.url0 = 'https://min-api.cryptocompare.com/data/histominute' + \
                    '?fsym=' + symbol + \
                    '&tsym=USD' + \
                    '&aggregate=1'
        self.url1 = 'https://min-api.cryptocompare.com/data/histohour' + \
                    '?fsym=' + symbol + \
                    '&tsym=USD'
        self.url2 = 'https://api.coinmarketcap.com/v2/ticker/' + CRYPTO_IDS[symbol]

        self.data = self.start_data()
        self.integration_order = self.get_integration_order()

        self.owned = 0
        self.avg_cost = None
        self.transaction_log = False

        # Attributes declared from Portfolio:
        #     -market_share
        #     -volume_24h_share
        #     -beta_st
        #     -beta_mt



    def start_data(self, limit=2000):

        try:
            res = requests.get(self.url0 + '&limit=' + str(limit), timeout=10)
            res.raise_for_status()
            data = res.json()['Data']
        except requests.exceptions.HTTPError:
            raise exceptions.ScrapeFailed()

        data = pd.DataFrame(data)
        data['time'] = [datetime.datetime.fromtimestamp(d) for d in data['time']]

        data['std_close'] = StandardScaler().fit_transform(data[['close']])

        return data

    def update_data(self, limit=10):

        # collect recent data
        try:
            res = requests.get(self.url0 + '&limit=' + str(limit), timeout=10)
            res.raise_for_status()
            data = res.json()['Data']
        except requests.exceptions.HTTPError:
            raise exceptions.ScrapeFailed()


        tmp_data = pd.DataFrame(data)
        tmp_data['time'] = [datetime.datetime.fromtimestamp(d) for d in tmp_data['time']]

        #reconcile recent data with past data
        tmp_new_data = self.data.merge(tmp_data, on=list(self.data), how='outer')
        tmp_new_data.drop_duplicates(subset=['time'], inplace=True, keep='last')
        tmp_new_data = tmp_new_data.sort_values('time').reset_index()

        #standardize the resulting dataframe's 'close' column
        tmp_new_data['std_close'] = StandardScaler().fit_transform(tmp_new_data[['close']])

        self.data = tmp_new_data

        return

    def get_market_data(self):

        # collect market data (market_cap and volume_24h)
        try:
            res = requests.get(self.url2, timeout=10)
            res.raise_for_status()
            data = res.json()['data']['quotes']['USD']
        except requests.exceptions.HTTPError:
            raise exceptions.ScrapeFailed()

        return data['market_cap'], data['volume_24h']

    def get_integration_order(self):

        result = [None, 1]
        count = 0
        while result[1] > .1:
            integrated = np.diff(self.data['close'].values, n=count)

            # tests for unit roots in individual time series using augmented Dickey-Fuller
            result = adfuller(integrated,
                              autolag=None,
                              maxlag=1,
                              regresults=True)

            ic_best= result[3].icbest
            used_lag = result[3].usedlag

            count += 1

            # code below returns the IC statistics from the autolag method if used
            # tmp = {}
            # for lag in result[3].autolag_results:
            #     tmp[lag] = result[3].autolag_results[lag].aic

        order = count - 1

        return order

    def get_returns_st(self, interval):
        tmp_data = self.data.loc[self.data['time'].dt.minute == 0, 'close'].iloc[::interval]

        returns_data = [a1 / a2 - 1 for a1, a2 in zip(tmp_data[1:], tmp_data)]

        return returns_data


        #
        # data.loc[data['5. volume'] == 0, '5. volume']

    def get_returns_mt(self, interval, limit):
        # use the cryptocompare api to call last 10 days
        try:
            res = requests.get(self.url1 + \
                               '&aggregate=' + str(interval) + \
                               '&limit=' + str(limit), timeout=10)
            res.raise_for_status()
            data = res.json()['Data']
        except requests.exceptions.HTTPError:
            raise exceptions.ScrapeFailed()

        data = pd.DataFrame(data)
        data['time'] = [datetime.datetime.fromtimestamp(d) for d in data['time']]

        tmp_data = data['close']

        returns_data = [a1 / a2 - 1 for a1, a2 in zip(tmp_data[1:], tmp_data)]

        return returns_data
