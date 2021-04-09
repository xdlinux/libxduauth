import time
from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs
from ..utils.vcode import _process_vcode
from ..utils.aes import encrypt


class IDSSession(AuthSession):
    cookie_name = 'ids'

    def __init__(
            self, target, username, password,
            *args, **kwargs
    ):
        super().__init__(f'{self.cookie_name}_{username}')
        if self.is_logged_in():
            return
        else:
            self.cookies.clear()
        page = self.get(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target, 'type': 'userNameLogin'}
        ).text
        is_need_captcha, vcode = self.get(
            'https://ids.xidian.edu.cn/authserver/checkNeedCaptcha.htl',
            params={'username': username, '_': int(time.time() * 1000)}
        ).json()['isNeed'], None
        if is_need_captcha:
            captcha = self.get(
                'http://ids.xidian.edu.cn/authserver/getCaptcha.htl',
                params={str(int(time.time() * 1000)): ''}
            )
            _process_vcode(Image.open(BytesIO(captcha.content))).show()
            vcode = input('验证码：')
        page = BeautifulSoup(page, "lxml")
        form = page.findChild(attrs={'id': 'pwdFromId'})
        params = parse_form_hidden_inputs(form)
        enc = form.find('input', id='pwdEncryptSalt').get('value')
        self.post(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target},
            data=dict(params, **{
                'username': username,
                'password': encrypt(password.encode(), enc.encode()),
                'captcha': vcode,
                'rememberMe': 'true'
            })
        )

    def is_logged_in(self):
        return self.get(
            'http://ids.xidian.edu.cn/authserver/index.do',
            allow_redirects=False
        ).status_code != 302
