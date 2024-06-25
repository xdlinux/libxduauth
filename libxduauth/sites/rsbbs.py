from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs
from ..utils.vcode import get_solver


class RSBBSSession(AuthSession):
    HOST = 'rsbbs.xidian.edu.cn'
    cookie_name = 'rsbbs'

    def __init__(self, username, password):
        super().__init__(f'{self.cookie_name}_{username}')
        if not self.is_loggedin():
            self.login(username, password)

    def login(self, username, password):
        login = self.get(f'http://{self.HOST}/member.php', params={
            'mod': 'logging',
            'action': 'login',
            'mobile': '2'
        })
        soup = BeautifulSoup(login.text, 'lxml')

        img = soup.find('img', {'class': 'seccodeimg'}).get('src')
        vcode = get_solver('rsbbs.xidian.edu.cn')(self.get(f'http://{self.HOST}/{img}', headers={
            'Referer': login.url
        }).content)
        page = self.post(
            f'http://{self.HOST}/' +
            soup.find('form', id='loginform').get('action'), data=dict(
                parse_form_hidden_inputs(soup), **{
                    'username': username,
                    'password': password,
                    'questionid': '0',
                    'answer': '',
                    'seccodeverify': vcode,
                }
            )
        ).text
        if '欢迎您回来' not in page:
            return self.login(username, password)
        return

    def is_loggedin(self):
        return self.get(f'http://{self.HOST}/home.php', params={
            'mod': 'space', 'do': 'profile'
        }, allow_redirects=False).status_code != 302
