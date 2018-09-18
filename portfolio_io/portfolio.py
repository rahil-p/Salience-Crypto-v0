import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import numpy as np
import pandas as pd

import requests
from datetime import datetime
from itertools import combinations

from pair_io.pair import Pair
from crypto_io.crypto import Crypto
import config

class Portfolio:

    def __init__(self, cap, crypto_symbols):

        self.cap = cap
        self.cryptos = [Crypto(x) for x in crypto_symbols]

        plotly.tools.set_credentials_file(username='sentience', api_key=config.plotly_api_key)
        self.link = self.plot_cryptos()

        self.url0 = 'https://api.coinmarketcap.com/v2/global/'
        self.total_market_cap, self.total_volume_24h = self.get_global_data()

        self.set_market_data_cryptos()
        self.set_betas_st_cryptos()
        self.set_betas_mt_cryptos()

        self.pair_options = self.get_pairs()
        self.pairs_df = self.get_pairs_df()

        self.manager = None

    def get_global_data(self):
        try:
            res = requests.get(self.url0, timeout=10)
            res.raise_for_status()
            data = res.json()['data']['quotes']['USD']
        except requests.exceptions.HTTPError:
            raise exceptions.ScrapeFailed()

        return data['total_market_cap'], data['total_volume_24h']

    def update_cryptos(self):

        for crypto in self.cryptos:
            crypto.update_data()

    def plot_cryptos(self, switch=0):

        if switch == 0:
            return

        traces = []
        for crypto in self.cryptos:
            traces.append(go.Scatter(x=crypto.data['time'],
                                     y=crypto.data['std_close'],
                                     name=crypto.symbol,
                                     hoverinfo='y',
                                     line=dict(color=crypto.color),
                                     opacity=.8))

        layout = go.Layout(title='Sentience Crypto - Portfolio',
                           xaxis=dict(title='time'),
                           yaxis=dict(title='USD ($)'))

        fig = go.Figure(traces, layout=layout)

        try:
            link = py.plot(fig, filename='sc_portfolio', auto_open=False)
        except plotly.exceptions.PlotlyRequestError:
            print('PlotlyRequestError:')
            return 'https://plot.ly/products/cloud'

        return link

    # ----- (coinmarketcap)

    def set_market_data_cryptos(self):

        for crypto in self.cryptos:
            cap, vol = crypto.get_market_data()
            crypto.market_share = cap / self.total_market_cap
            crypto.volume_24h_share =  vol / self.total_volume_24h

        return

    # ----- (mt: 10d w/ 6hr intervals; st: 2000m w/ 1m intervals)

    def set_sharpe_ratios_mt_cryptos(self):

        pass

    def set_betas_st_cryptos(self, market_returns='ew_mean'):

        returns_df = self.collect_returns_st_cryptos(interval=1)

        for crypto in self.cryptos:
            covariance = np.cov(returns_df[crypto.symbol], returns_df[market_returns])[0][1]
            crypto.beta_st = covariance / np.var(returns_df[crypto.symbol])

        return

    def set_betas_mt_cryptos(self, market_returns='ew_mean'):

        # 10-day, 6hr returns-based (cryptocompare)
        returns_df = self.collect_returns_mt_cryptos(interval=6, limit=240)

        for crypto in self.cryptos:
            covariance = np.cov(returns_df[crypto.symbol], returns_df[market_returns])[0][1]
            crypto.beta_mt = covariance / np.var(returns_df[crypto.symbol])

        return

    def collect_returns_st_cryptos(self, interval=1):

        returns_df = pd.DataFrame()
        for crypto in self.cryptos:
            returns_df[crypto.symbol] = crypto.get_returns_st(interval=interval)

        returns_df['ew_mean'] = returns_df.mean(axis=1)

        return returns_df

    def collect_returns_mt_cryptos(self, interval=6, limit=240):

        # 10-day, 6hr returns-based (cryptocompare)
        returns_df = pd.DataFrame()
        for crypto in self.cryptos:
            returns_df[crypto.symbol] = crypto.get_returns_mt(interval=interval, limit=limit)

        returns_df['ew_mean'] = returns_df.mean(axis=1)

        return returns_df

    # -----

    def get_cryptos_df(self):

        pass

    def get_pairs(self):

        pairs = [Pair(pair) for pair in combinations(self.cryptos, 2) \
                            if (pair[0].leverages or pair[1].leverages)]

        return pairs

    def get_pairs_df(self):

        summary = pd.DataFrame(columns=['pearson r', 'pearson p', 'spearman r', 'spearman p', 'I(d)', 'coint p',
                                        'spread_mean', 'spread_std', 'spread I(d)',
                                        'beta_st_diff', 'beta_st_pair', 'beta_mt_diff', 'beta_mt_pair',
                                        'share_ratio', 'share_pair',
                                        'volume_ratio', 'volume_pair',
                                        'exchange_rate'])

        [pair.add_summary_df_row(summary) for pair in self.pair_options]

        return summary







# pair scoring & selection
# get time to convergence when divergence first is greater than e.g. [.5, .75, 1.0] (for each pair)

# Summary:
#     -only hold one short and one long position at any given moment

# Outline:
#     -if no short and long positions are held at a given moment:
#         -collect pairs for which the spread threshold has been surpassed
#         -select the pair with optimal factors
#          (add consideration of time to convergence & spread distance)
#          (in the time_window, e.g. # of times inner and outer thresholds are hit, time since inner threshold hit)
#             -place orders with stop conditions
#             -exit positions when some inner threshold is met
#                 -increase threshold by x every n minutes (to force quicker position)


# Manager object:       ~created for any new trade (None if inactive); killed when positions are closed
#     -self.status: {short: ..., long: ...}
#     -
