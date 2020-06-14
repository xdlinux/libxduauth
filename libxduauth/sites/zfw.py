import re

from bs4 import BeautifulSoup
from requests import Session


class ZFWSession(Session):
    BASE = 'https://zfw.xidian.edu.cn'

    def __init__(self, username, password, *args, **kwargs):
        super(ZFWSession, self).__init__(*args, **kwargs)
        self.headers.update({
            'User-Agent': 'Mobile'
        })
        soup = BeautifulSoup(self.get(self.BASE).text, "lxml")
        vcv = soup.find('input', type='hidden').get('value')
        error = re.findall(
            r'请修复以下错误<\/p><ul><li>(.*?)<',
            self.post(self.BASE + '/login', data={
                "LoginForm[username]": username,
                "LoginForm[password]": password,
                "_csrf": vcv,
                "login-button": ""
            }).text
        )
        self.headers.pop('User-Agent')
        if len(error) > 0:
            raise ConnectionError(error[0])
