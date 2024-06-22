import json
from base64 import b64encode, b64decode
from io import BytesIO
from re import search

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from PIL import Image

from ..AuthSession import AuthSession
from ..utils.vcode import _image_to_ascii


def encrypt(password, key):
    if type(password) is str:
        password = password.encode('utf-8')
    if type(key) is str:
        key = key.encode('utf-8')
    crypt = AES.new(key, AES.MODE_ECB)
    return b64encode(crypt.encrypt(pad(password, 16))).decode('utf-8')


def _captcha_solver(img):
    img.show()
    return input('Input captcha vcode: ')


def _captcha_solver_cli(img):
    print(_image_to_ascii(img, (80, 16)))
    return input('Input captcha vcode: ')


class XKSession(AuthSession):
    BASE = 'https://xk.xidian.edu.cn/xsxk'
    cookie_name = 'xk'
    user = {}
    current_batch = {}
    captcha_solver = None

    def __init__(self, username, password, keyword='', captcha_solver=_captcha_solver):
        if callable(captcha_solver):
            self.captcha_solver = captcha_solver
        super().__init__(f'{self.cookie_name}_{username}')
        self.username = username
        cookies = requests.utils.dict_from_cookiejar(self.cookies)
        if 'token' in cookies and 'batch' in cookies:
            self.headers.update({'Authorization': cookies['token']})
            self.current_batch = json.loads(cookies['batch'])
        if 'token' not in cookies or 'batch' not in cookies or not self.is_logged_in():
            self.persist('token', self.login(username, password))
            batches = [
                b for b in self.user['electiveBatchList']
                if b['canSelect'] == '1'
	    ]
            key_batches = [b for b in batches if keyword in b['name']]
            if not len(key_batches):
                raise ValueError(f'''Keyword '{keyword}' is unavailable. Available ones are: {
                    ', '.join(repr(b['name']) for b in batches)
		}''')
            self.current_batch = key_batches[0]
            self.persist('batch', json.dumps(self.current_batch))
            cookie_token = next(c for c in self.cookies if c.name == 'token')
            self.persist('Authorization', cookie_token.value)
            self.get(self.BASE + '/elective/grablessons', params={
                'batchId': self.current_batch['code'],
            })  # wierd, yet mandatory.
            self.headers.update({'Authorization': cookie_token.value})

    def persist(self, name, value):
        self.cookies.set_cookie(requests.cookies.create_cookie(
            domain='xk.xidian.edu.cn', path='/nowhere', name=name, value=value,
        ))
        self.cookies.save(ignore_discard=True)

    def login(self, username, password):
        self.headers.update({'Authorization': ''})
        index = self.get(self.BASE + '/xsxk/profile/index.html').text
        key = search(r'loginForm\.aesKey = "([a-zA-Z0-9=]*)";', index)
        if not key:  # 应当不会出现 index.html 中没有 aeskey 的情况
            raise RuntimeError('AES Key Not Found')
        key = key.groups()[0]

        for _ in range(3):
            resp = self.post(self.BASE + '/auth/captcha')
            captcha = resp.json()['data']
            vcode = self.captcha_solver(Image.open(BytesIO(
                b64decode(captcha['captcha'][22:])
            ))) # 'data:image/png;base64,' stripped

            login_resp = self.post(f'{self.BASE}/auth/login', data={
                'loginname': username,
                'password': encrypt(password, key),
                'captcha': vcode,
                'uuid': captcha['uuid']
            }).json()
            if login_resp['code'] == 200:
                self.user = login_resp['data']['student']
                return login_resp['data']['token']
        raise RuntimeError(login_resp['msg'])

    def is_logged_in(self):
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
