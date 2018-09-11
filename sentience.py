from robinhood_io.rh import Robinhood


def main():
    rh = Robinhood()
    rh.login()

    power = rh.get_power()
    print('Available buying power: ' + power)

    x = rh.order_crypto('BTC', 'market', 'buy', '.08', 1)
    print(x)

    rh.logout()

if __name__ == '__main__':
    main()
