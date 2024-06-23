import time
from io import BytesIO
from base64 import b64decode

from PIL import Image
from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs
from ..utils.aes import encrypt
from ..utils.vcode import _solve_slider_captcha


def _captcha_solver(big_img, small_img):
    big_img.show()
    return input('Input captcha vcode: ')


def _captcha_solver_auto(big_img, small_img):
    return _solve_slider_captcha(big_img, small_img) * 280 // big_img.width


def _dynamic_solver():
    return input('Input dynamic code: ')


class IDSSession(AuthSession):
    target = 'https://ids.xidian.edu.cn/personalInfo/personCenter/index.html'
    type = 'userNameLogin'
    cookie_name = 'ids'
    captcha_solver = dynamic_solver = None
    __secrets = {}

    def __init__(
        self, target=None, type=None,
        username=None, password=None, cookies=None,
        captcha_solver=_captcha_solver, dynamic_solver=_dynamic_solver
    ):
        if not callable(captcha_solver) or not callable(dynamic_solver):
            raise TypeError('``captcha_solver`` or ``dynamic_solver`` is not callable')
        super().__init__(f'{self.cookie_name}_{username}')
        if self.is_logged_in():
            return
        self.captcha_solver, self.dynamic_solver = captcha_solver, dynamic_solver
        if target:
            self.target = target
        # supported login types: 'userNameLogin' and 'dynamicLogin'
        if type:
            self.type = type
        self.cookies.clear()
        self.__secrets = {
            'username': username, 'password': password, 'cookies': cookies
        }
        self.login()

    def login(self):
        # general login
        # login with cookies if given
        if self.__secrets['cookies']:
            return self.login_cookies(self.__secrets['cookies'])
        # prepare login params
        if not self.login_prepare():
            return False
        username = self.__secrets['username']
        if not username:
            return False
        # solve captcha for up to 3 trials
        if self.is_captcha_needed(username):
            verify = False
            for _ in range(3):
                if self.captcha_submit(self.captcha_solver(*map(
                    lambda s: Image.open(BytesIO(b64decode(s))),
                    self.captcha_get()
                ))):
                    verify = True
                    break
            if not verify:
                return False
        # username login
        if self.type == 'userNameLogin':
            return self.login_username_finish(
                username=username, password=self.__secrets['password']
	    )
        # dynamic login
        elif self.type == 'dynamicLogin':
            if not self.login_dynamic_send_code(username=username):
                return False
            return self.login_dynamic_finish(
                username=username, password=self.dynamic_solver()
	    )
        return False

    def is_captcha_needed(self, username):
        # check if captcha is needed
        return self.get(
            'https://ids.xidian.edu.cn/authserver/checkNeedCaptcha.htl',
            params={'username': username, '_': f'{int(time.time() * 1000)}'}
        ).json()['isNeed']

    def captcha_get(self):
        # get captcha images in base64
        data = self.get(
            'https://ids.xidian.edu.cn/authserver/common/openSliderCaptcha.htl',
            params={'_': f'{int(time.time() * 1000)}'}
        ).json()
        return data['bigImage'], data['smallImage']

    def captcha_submit(self, vcode):
        # submit captcha verification code
        # vcode (move length) should be
        # slider_offset_to_the_left * 280 // background_width
        return self.post(
            'https://ids.xidian.edu.cn/authserver/common/verifySliderCaptcha.htl',
            data={'canvasLength': '280', 'moveLength': f'{vcode}'}
        ).json()['errorMsg'] == 'success'

    def login_prepare(self):
        # prepare params for logging in
        page = self.get(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': self.target, 'type': self.type}
        ).text
        page = BeautifulSoup(page, 'lxml')
        form = page.findChild(attrs={'id': 'pwdFromId'})
        enc = form.find('input', id='pwdEncryptSalt').get('value')
        params = parse_form_hidden_inputs(form)
        params.update({'captcha': '', 'cllt': self.type, 'rememberMe': 'true'})
        self.__secrets.update({'params': params, 'enc': enc})
        return True

    def login_username_finish(self, username, password):
        password = encrypt(password.encode(), self.__secrets['enc'].encode())
        return self.post(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': self.target}, data=dict(
                self.__secrets['params'],
                **{'username': username, 'password': password}
            )
        ).status_code == 200

    def login_dynamic_send_code(self, username):
        # send dynamic code to the username (phone number)
        res = self.post(
            'https://ids.xidian.edu.cn/authserver/dynamicCode/getDynamicCode.htl',
            data={'mobile': username, 'captcha': ''}
        )
        return (
            res.status_code == 200 and
            res.json()['code'] in ('success', 'timeExpire')
	)

    def login_dynamic_finish(self, username, password):
        # finish dynamic login with username (phone number)
        # and password (dynamic code)
        # these two keys is parsed by bs4 in login_prepare
        # remove them otherwise dynamic login will fail
        self.__secrets['params'].pop('password', None)
        self.__secrets['params'].pop(None, None)
        return self.post(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': self.target}, data=dict(
                self.__secrets['params'],
                **{'username': username, 'dynamicCode': password}
            )
        ).status_code == 200

    def login_cookies(self, cookies=None):
        # login with cookies
        if self.get(
            'https://ids.xidian.edu.cn/personalInfo/personCenter/index.html',
            cookies=cookies or self.cookies, allow_redirects=False
        ).status_code != 302:
            # update cookies if given
            if cookies:
                self.cookies.update(cookies)
            return True
        return False

    def is_logged_in(self):
        # check login state
        return self.login_cookies(cookies=None)
