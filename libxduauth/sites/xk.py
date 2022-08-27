import json
from base64 import b64encode, b64decode
from io import BytesIO
from re import search

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from PIL import Image

from ..AuthSession import AuthSession


def encrypt(password, key):
    if type(password) is str:
        password = password.encode('utf-8')
    if type(key) is str:
        key = key.encode('utf-8')
    crypt = AES.new(key, AES.MODE_ECB)
    return b64encode(crypt.encrypt(pad(password, 16))).decode('utf-8')


class XKSession(AuthSession):
    BASE = 'https://xk.xidian.edu.cn/xsxk'
    cookie_name = 'xk'
    user = {}
    current_batch = {}

    def __init__(self, username, password, keyword=''):
        super().__init__(f'{self.cookie_name}_{username}')
        self.username = username
        cookies = requests.utils.dict_from_cookiejar(self.cookies)
        if 'token' in cookies and 'batch' in cookies:
            self.headers.update({'Authorization': cookies['token']})
            self.current_batch = json.loads(cookies['batch'])
        if 'token' not in cookies or 'batch' not in cookies or not self.is_loggedin():
            self.persist('token', self.login(username, password))
            self.current_batch = next(filter(
                lambda batch: (
                    batch['canSelect'] == '1' and
                    keyword in batch['name']
                ),
                self.user['electiveBatchList']
            ))
            self.persist('batch', json.dumps(self.current_batch))
            cookies = requests.utils.dict_from_cookiejar(self.cookies)
            self.cookies.update({'Authorization': cookies['token']})
            self.get(self.BASE + '/elective/grablessons', params={
                'batchId': self.current_batch['code'],
            })  # wierd, yet mandatory.
            self.headers.update({'Authorization': cookies['token']})

    def persist(self, name, value):
        self.cookies.set_cookie(requests.cookies.create_cookie(
            domain='xk.xidian.edu.cn', path='/nowhere',
            name=name, value=value,
        ))
        self.cookies.save(ignore_discard=True)

    def login(self, username, password):
        self.headers.update({'Authorization': ''})
        index = self.get(self.BASE + '/xsxk/profile/index.html').text
        key = search(r'loginForm\.aesKey = "([a-zA-Z0-9=]*)";', index)
        if not key:  # 应当不会出现 index.html 中没有 aeskey 的情况
            raise RuntimeError('AES Key Not Found')
        key = key.groups()[0]

        resp = self.post(self.BASE + '/auth/captcha')
        captcha = resp.json()['data']

        # show captcha
        captcha_img = captcha['captcha'][22:]  # data:image/png;base64,
        Image.open(BytesIO(b64decode(captcha_img))).show()

        # TODO:input function shouldn't exist here
        captcha_code = input('验证码：')

        login_resp = self.post(f'{self.BASE}/auth/login', data={
            'loginname': username,
            'password': encrypt(password, key),
            'captcha': captcha_code,
            'uuid': captcha['uuid']
        }).json()
        if login_resp['code'] != 200:
            raise RuntimeError(login_resp['msg'])
        self.user = login_resp['data']['student']
        return login_resp['data']['token']

    def is_loggedin(self):
        try:
            info = self.post(f'{self.BASE}/elective/user', data={
                'batchId': self.current_batch['code'],
            }).json()
        except requests.JSONDecodeError:
            return False
        if info['code'] == 200:
            self.user = info['data']['student']
            return True
        return False
