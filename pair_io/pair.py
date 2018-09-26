import numpy as np
import pandas as pd
from scipy.stats.stats import pearsonr
from scipy.stats.stats import spearmanr
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller

class Pair:

    def __init__(self, pair):
        self.cryptos_pair = tuple(pair)
        self.symbols_pair = tuple([crypto.symbol for crypto in self.cryptos_pair])
        self.name = '-'.join(self.symbols_pair)
        self.pair_type = self.get_pair_type()

        self.integration_orders_pair = self.get_integration_orders()
        self.correlation_pearson = self.get_correlation_pearson()       # [r, pval] for a Pearson correlation
        self.correlation_spearman = self.get_correlation_spearman()     # [r, pval] for a Spearman correlation
        self.cointegration = self.get_cointegration()                   # pval of an Engle-Granger two-step cointegration test

        self.beta_st_diff, self.beta_mt_diff = self.get_difference_betas()

        self.market_share_ratio = self.get_ratio_market_share()
        self.volume_24h_share_ratio = self.get_ratio_volume_24h()
        self.exchange_rate = self.get_exchange_rate()

        self.spread = self.get_spread()
        self.spread_mean = np.mean(self.spread)
        self.spread_std = np.std(self.spread)
        self.spread_integration_order = self.get_spread_integration_order()
        self.threshold = 0


    def add_summary_df_row(self, df):

        df.loc['-'.join(self.symbols_pair)] = pd.Series({'pearson r': self.correlation_pearson[0],
                                                         'pearson p': self.correlation_pearson[1],
                                                         'spearman r': self.correlation_spearman[0],
                                                         'spearman p': self.correlation_spearman[1],
                                                         'I(d)': self.integration_orders_pair,
                                                         'coint p': self.cointegration,
                                                         'spread_mean': self.spread_mean,
                                                         'spread_std': self.spread_std,
                                                         'spread I(d)': self.spread_integration_order,
                                                         'beta_st_diff': self.beta_st_diff,
                                                         'beta_st_pair': (self.cryptos_pair[0].beta_st,
                                                                          self.cryptos_pair[1].beta_st),
                                                         'beta_mt_diff': self.beta_mt_diff,
                                                         'beta_mt_pair': (self.cryptos_pair[0].beta_mt,
                                                                          self.cryptos_pair[1].beta_mt),
                                                         'share_ratio': self.market_share_ratio,
                                                         'share_pair': (self.cryptos_pair[0].market_share,
                                                                        self.cryptos_pair[1].market_share),
                                                         'volume_ratio': self.volume_24h_share_ratio,
                                                         'volume_pair': (self.cryptos_pair[0].volume_24h_share,
                                                                         self.cryptos_pair[1].volume_24h_share),
                                                         'exchange_rate': self.exchange_rate})

        return df

    def get_correlation_pearson(self):

        correlation = pearsonr(self.cryptos_pair[0].data['close'].values,
                               self.cryptos_pair[1].data['close'].values)

        return correlation

    def get_correlation_spearman(self):

        correlation = spearmanr(self.cryptos_pair[0].data['close'].values,
                                self.cryptos_pair[1].data['close'].values)

        return correlation

    def get_cointegration(self):

        cointegration = coint(self.cryptos_pair[0].data['close'].values,
                              self.cryptos_pair[1].data['close'].values)

        return cointegration[1]

    def get_integration_orders(self):

        return [self.cryptos_pair[0].integration_order,
                self.cryptos_pair[1].integration_order]

    def get_difference_betas(self):

        # absolute differences for each beta type
        diff_st = abs(self.cryptos_pair[1].beta_st - self.cryptos_pair[0].beta_st)
        diff_mt = abs(self.cryptos_pair[1].beta_mt - self.cryptos_pair[0].beta_mt)

        return diff_st, diff_mt

    def get_ratio_market_share(self):

        # max ratio between market shares
        return np.max([self.cryptos_pair[0].market_share, self.cryptos_pair[1].market_share]) / \
               np.min([self.cryptos_pair[0].market_share, self.cryptos_pair[1].market_share])

    def get_ratio_volume_24h(self):

        # max ratio between daily volume shares
        return np.max([self.cryptos_pair[0].volume_24h_share, self.cryptos_pair[1].volume_24h_share]) / \
               np.min([self.cryptos_pair[0].volume_24h_share, self.cryptos_pair[1].volume_24h_share])

    def get_exchange_rate(self):

        # max exchange rate between the cryptos
        return np.max([self.cryptos_pair[0].data['close'].iloc[-1], self.cryptos_pair[1].data['close'].iloc[-1]]) / \
               np.min([self.cryptos_pair[0].data['close'].iloc[-1], self.cryptos_pair[1].data['close'].iloc[-1]])

    def get_pair_type(self):

        tmp = tuple(map(lambda lev: 1 if lev is not None else 0, [x.leverages for x in self.cryptos_pair]))

        return tmp

    # -----

    def get_spread(self, time_window=360):

        if time_window == None:
            tmp0 = StandardScaler().fit_transform(self.cryptos_pair[0].data['std_close'].values)
            tmp1 = StandardScaler().fit_transform(self.cryptos_pair[1].data['std_close'].values)
        else:
            tmp0 = StandardScaler().fit_transform(self.cryptos_pair[0].data.tail(time_window)[['std_close']].values)
            tmp1 = StandardScaler().fit_transform(self.cryptos_pair[1].data.tail(time_window)[['std_close']].values)

        return np.ravel(tmp0 - tmp1)

    def get_spread_integration_order(self):

        result = [None, 1]
        count = 0
        while result[1] > .05:
            integrated = np.diff(self.spread, n=count)

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

    # -----

    def get_outer_thresholds(self):
        pass

    def get_inner_thresholds(self):
        pass
