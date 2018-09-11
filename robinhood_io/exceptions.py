class RobinhoodException(Exception):
    pass

class LoginFailed(RobinhoodException):
    pass

class LogoutFailed(RobinhoodException):
    pass

class AccessFailed(RobinhoodException):
    pass

class OrderFailed(RobinhoodException):
    pass
