import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from portfolio_io.portfolio import Portfolio
from pair_io.pair import Pair
from crypto_io.crypto import Crypto

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def main():

    start = time.time()

    # ensure sufficient cap given pricing of argued
    s = Portfolio(250, ['XBT', 'ETH', 'ETC', 'XMR', 'REP', 'LTC'])

    if s.link is not None:
        print(s.link)


    print(s.pairs_df.iloc[:, :9])
    print(s.pairs_df.iloc[:, 9:])

    end = time.time()

    for pair in s.pair_options:

        fit = np.polyfit(np.arange(0,len(pair.spread)), pair.spread, 1)
        fit_fn = np.poly1d(fit)
        print(fit)
        print(fit_fn)

        sns.set_style('darkgrid')
        plt.plot(pair.spread)
        plt.plot(fit_fn(np.arange(0,len(pair.spread))))
        plt.title('-'.join(pair.symbols_pair))
        plt.xticks(np.arange(0, len(pair.spread) + 60, 60))
        plt.axhline(0, color='grey')
        plt.show()

    # time.sleep(120)
    #
    # s.update_cryptos()
    # for crypto in s.cryptos:
    #     print(crypto.data)


    print(end - start)

if __name__ == '__main__':
    main()
