

class Kraken:

    def __init__(self):

        self.headers = {}

        self.api_session = requests.session()
        self.api_session.headers = self.headers
