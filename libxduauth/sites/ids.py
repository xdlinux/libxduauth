from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs
from ..utils.aes import encrypt


class IDSSession(AuthSession):

    def __init__(
            self, target, username, password,
            *args, **kwargs
    ):
        super(IDSSession, self).__init__('ids')
        if self.is_logged_in():
            return
        else:
            self.cookies.clear()
        page = self.get(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target}
        ).text
        page = BeautifulSoup(page, "lxml")
        params = parse_form_hidden_inputs(page)
        enc = page.find('input', id='pwdDefaultEncryptSalt').get('value')
        self.post(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target},
            data=dict(params, **{
                'username': username,
                'password': encrypt(password.encode(), enc.encode()),
                'rememberMe': 'on'
            })
        )

    def is_logged_in(self):
        return self.get(
            'http://ids.xidian.edu.cn/authserver/index.do',
            allow_redirects=False
        ).status_code != 302
