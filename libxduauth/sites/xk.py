import base64
import json
import time
from io import BytesIO

import requests
from PIL import Image

from ..AuthSession import AuthSession
from ..utils.des import encrypt


class XKSession(AuthSession):
    BASE = 'http://xk.xidian.edu.cn/xsxkapp/sys/xsxkapp'
    DESKeys = ['this', 'password', 'is']

    def __init__(self, username, password):
        super().__init__('xk')
        self.username = username
        cookies = requests.utils.dict_from_cookiejar(self.cookies)
        if 'token' in cookies:
            self.headers.update({'token': cookies['token']})
        if 'token' not in cookies or not self.is_loggedin():
            token = requests.cookies.create_cookie(
                domain='xk.xidian.edu.cn', path='/nowhere',
                name='token', value=self.login(username, password)
            )
            self.cookies.set_cookie(token)
            cookies = requests.utils.dict_from_cookiejar(self.cookies)
            self.headers.update({'token': cookies['token']})
        self.token = cookies['token']
        self.cookies.save(ignore_discard=True)

    def login(self, username, password):
        resp = self.get(self.BASE + '/student/4/vcode.do',
                        params={'timestamp': int(time.time() * 1000)})
        captcha_token = resp.json()['data']['token']

        # show captcha
        captcha_resp = self.get(
            self.BASE + '/student/vcode/image.do',
            params={'vtoken': captcha_token}
        )
        Image.open(BytesIO(captcha_resp.content)).show()

        # TODO:input function shouldn't exist here
        captcha_code = input('验证码：')

        login_resp = self.get(
            f'{self.BASE}/student/check/login.do',
            params={
                'timestamp': int(time.time() * 1000),
                'loginName': username,
                'loginPwd': base64.b64encode(
                    encrypt(password, self.DESKeys).encode()
                ).decode(),
                'verifyCode': captcha_code,
                'vtoken': captcha_token
            }
        )
        print(login_resp.json()['msg'])
        return login_resp.json()['data']['token']

    def is_loggedin(self):
        try:
            info = self.get(f'{self.BASE}/student/{self.username}.do', params={
                'timestamp': int(time.time() * 1000),
            }).json()
        except json.JSONDecodeError:
            return False
        if info['code'] == '1':
            self.info = info['data']
            return True
        return False
