class CryptoException(Exception):
    pass

class ScrapeFailed(CryptoException):
    pass

class CointegrationException(CryptoException):
    pass
