import time

from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs
from ..utils.aes import encrypt
from ..utils.vcode import get_solver


class IDSSession(AuthSession):
    cookie_name = 'ids'

    def __init__(self, target, username, password):
        super().__init__(f'{self.cookie_name}_{username}')
        if self.is_logged_in():
            return
        else:
            self.cookies.clear()
        page = self.get(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target}
        ).text
        while self.get(
            'https://ids.xidian.edu.cn/authserver/checkNeedCaptcha.htl',
            params={'username': username, '_': str(int(time.time() * 1000))}
        ).json()['isNeed']:
            if self.post(
                'https://ids.xidian.edu.cn/authserver/common/verifySliderCaptcha.htl',
                data={
                    # canvasLength: canvas宽度, 硬编码280
                    'canvasLength': '280',
                    # moveLength: 按比例缩放后的滑块位移, 有容错
                    'moveLength': str(get_solver('ids.xidian.edu.cn')(self.get(
                        'https://ids.xidian.edu.cn/authserver/common/openSliderCaptcha.htl',
                        params={'_': str(int(time.time() * 1000))}
                    ).json()))
                }
            ).json()['errorMsg'] == 'success':
                break
            # 返回: {
            #     'errorCode': ..., # 验证通过时为1
            #     'errorMsg': ... # 验证通过时为'success'
            # }
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
                'captcha': '',
                'rememberMe': 'true'
            })
        )

    def is_logged_in(self):
        return self.get(
            'http://ids.xidian.edu.cn/authserver/index.do',
            allow_redirects=False
        ).status_code != 302
