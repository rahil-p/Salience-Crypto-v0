CRYPTO_NAMES = {'XBT': 'Bitcoin',           # confirm if discrepencies are sourced from CME vs. CFE
                'ETH': 'Ethereum',
                'ETC': 'Ethereum Classic',
                'XMR': 'Monero',
                #
                'BCH': 'Bitcoin Cash',
                'DASH': 'Dash',
                'EOS': 'EOS',
                'GNO': 'Gnosis',
                'ZEC': 'Zcash',
                'LTC': 'Litecoin',
                'REP': 'Augur',
                'XLM': 'Stellar',
                'XRP': 'Ripple'}

# UPDATE
CRYPTO_COLORS = {'XBT': '#329239',          # add the others (right now randomized in portfolio.py)
                 'ETH': '#C99D66',
                 'ETC': '#669073',
                 'XMR': '#FF6600'}

# for coinmarketcap API
CRYPTO_IDS = {'XBT': '1',                   # symbol used is BTC (non-issue b/c of id)
              'ETH': '1027',
              'ETC': '1321',
              'XMR': '328',
              #
              'BCH': '1831',
              'DASH': '131',
              'EOS': '1765',
              'GNO': '1659',
              'ZEC': '1437',
              'LTC': '2',
              'REP': '1104',
              'XLM': '512',
              'XRP': '52'}

# https://support.kraken.com/hc/en-us/articles/227876608-Which-currency-pairs-can-I-trade-on-margin-
CRYPTO_LEVERAGES = {'XBT': [2, 3, 4, 5],
                    'ETH': [2, 3, 4, 5],
                    'ETC': [2],
                    'XMR': [2]}
