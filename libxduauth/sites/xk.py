from ..AuthSession import AuthSession
from ..utils.des import encrypt
from PIL import Image
from io import BytesIO
import time
import base64


class XKSession(AuthSession):
    BASE = 'http://xk.xidian.edu.cn/xsxkapp/sys/xsxkapp'
    DESKeys = ['this', 'password', 'is']

    def __init__(self, username, password):
        super().__init__('xk')
        if not self.is_loggedin():
            self.token = self.login(username, password)

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
            self.BASE + '/student/check/login.do',
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
        return self.get(self.BASE + '/publicinfo/onlineUsers.do', params={
            'timestamp': int(time.time() * 1000),
        }).status_code == 200
