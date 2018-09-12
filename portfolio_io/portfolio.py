from crypto_io.crypto import Crypto

class Portfolio:

    def __init__(self, cap, crypto_symbols):

        self.cap = cap
        self.cryptos = [Crypto(x) for x in crypto_symbols]

    def update_cryptos(self):

        for crypto in self.cryptos:
            crypto.update_data()
