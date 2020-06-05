import http.cookiejar
import os

from requests import Session


# noinspection PyTypeChecker
class AuthSession(Session):
    def __init__(self, filename):
        self.cookie_path = os.path.expanduser(os.path.join('~', '.xduauth', 'cookies', filename))
        os.makedirs(os.path.dirname(self.cookie_path), exist_ok=True)
        super().__init__()
        self.cookies = http.cookiejar.LWPCookieJar(self.cookie_path)
        if not os.path.exists(self.cookie_path):
            self.cookies.save()
        self.cookies.load()

    def request(self, *args, **kwargs):
        ret = super().request(*args, **kwargs)
        self.cookies.save()
        return ret
