import time

from robinhood_io.rh import Robinhood
from portfolio_io.portfolio import Portfolio
from crypto_io.crypto import Crypto

def main1():

    rh = Robinhood()
    rh.login()
    rh.migrate_token()

    power = rh.get_power()
    print('Available buying power: ' + power)

    s = rh.order_crypto('BTC', 'market', 'buy', '.08', 1)
    print(s)

    rh.logout()

def main2():

    s = Portfolio(12, ['ETC', 'BTC'])

    print(s.cap)
    print('-----')

    for crypto in s.cryptos:
        print(crypto.symbol)
        print(crypto.name)
        print(crypto.data)
        print('-')

    time.sleep(120)

    for crypto in s.cryptos:
        crypto.update_data()
        print(crypto.data)

if __name__ == '__main__':
    main2()
