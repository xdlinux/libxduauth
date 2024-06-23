from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs
from ..utils.vcode import _image_binarize, _image_to_ascii


def _captcha_solver(img):
    img.show()
    return input('Input captcha vcode: ')


def _captcha_solver_cli(img):
    print(_image_to_ascii(_image_binarize(img), (80, 21)))
    return input('Input captcha vcode: ')


class RSBBSSession(AuthSession):
    HOST = 'rsbbs.xidian.edu.cn'
    cookie_name = 'rsbbs'
    captcha_solver = None

    def __init__(self, username, password, captcha_solver=_captcha_solver):
        if not callable(captcha_solver):
            raise TypeError('``captcha_solver`` is not callable')
        self.captcha_solver = captcha_solver
        super().__init__(f'{self.cookie_name}_{username}')
        if not self.is_logged_in():
            self.login(username, password)

    def login(self, username, password):
        login = self.get(f'http://{self.HOST}/member.php', params={
            'mod': 'logging',
            'action': 'login',
            'mobile': '2'
        })
        soup = BeautifulSoup(login.text, 'lxml')

        img = soup.find('img', {'class': 'seccodeimg'}).get('src')
        img = Image.open(BytesIO(self.get(
            f'http://{self.HOST}/{img}',
            headers={'Referer': login.url}
        ).content))
        page = self.post(
            f'http://{self.HOST}/' +
            soup.find('form', id='loginform').get('action'), data=dict(
                parse_form_hidden_inputs(soup), **{
                    'username': username,
                    'password': password,
                    'questionid': '0',
                    'answer': '',
                    'seccodeverify': self.captcha_solver(img),
                }
            )
        ).text
        if '欢迎您回来' not in page:
            return self.login(username, password)
        return

    def is_logged_in(self):
        return self.get(f'http://{self.HOST}/home.php', params={
            'mod': 'space', 'do': 'profile'
        }, allow_redirects=False).status_code != 302
