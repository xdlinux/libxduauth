
from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.vcode import get_solver
from ..utils.rsa import rsa_encrypt_by_pkcs1

class ZFWSession(AuthSession):
    COOKIE_NAME = 'zfw'
    _BASE = 'zfw.xidian.edu.cn'
    BASE = f'https://{_BASE}'

    def __init__(self, username, password):
        super().__init__(
            f'{self.COOKIE_NAME}_{username}', headers={'User-Agent': 'Mobile'}
        )
        if self.is_logged_in():
            return
        else:
            self.cookies.clear()
        form = BeautifulSoup(
            self.get(self.BASE).text, 'lxml'
        ).findChild(attrs={'id': 'login-form'})
        headers = {
            **self.headers,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': form.find('input', attrs={'name': '_csrf-8800'}).get('value')
        }
        enc_password = rsa_encrypt_by_pkcs1(
            form.find('input', id='public').get('value'), password
        )
        data = {
            'LoginForm[username]': username,
            'LoginForm[password]': enc_password
        }
        for _ in range(5):
            data['LoginForm[verifyCode]'] = get_solver(self._BASE)(self.get(
                f'{self.BASE}/site/captcha'
            ).content)
            res = self.post(
                f'{self.BASE}/site/validate-user', headers=headers, data=data
            )
            if res.status_code == 200 or res.json()['success']:
                break
        else:
            raise ConnectionError('登录失败')
        res = self.post(self.BASE, headers=headers, data=data)
        if res.status_code != 302 and res.headers.get(
            'X-Redirect'
        ) != 'http://zfw.xidian.edu.cn/home':
            raise ConnectionError('登录失败')

    def is_logged_in(self):
        return self.get(
            f'{self.BASE}/login', allow_redirects=False
        ).status_code == 302
