from io import BytesIO
import re
import os
import importlib.resources

from requests import Session
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract


def try_get_vcode(img):
    with importlib.resources.path(__package__, 'ar.traineddata') as pkg_path:
        img = img.convert('L')
        try:
            vcode = pytesseract.image_to_string(
                img, lang='ar',
                config="--psm 7 digits --tessdata-dir " +
                os.path.dirname(pkg_path)
            )
        except:
            vcode = pytesseract.image_to_string(
                img, lang='eng', config="--psm 7 digits")
    return vcode


class ZFWSession(Session):
    BASE = 'https://zfw.xidian.edu.cn'

    def __init__(self, username, password, *args, **kwargs):
        while True:
            vcode = ''
            error = ''
            super(ZFWSession, self).__init__(*args, **kwargs)
            while len(vcode) is not 4:
                soup = BeautifulSoup(self.get(self.BASE).text, "lxml")
                img_url = self.BASE + \
                    soup.find('img', id='loginform-verifycode-image').get('src')
                vcv = soup.find('input', type='hidden').get('value')
                img = Image.open(BytesIO(self.get(img_url).content))
                vcode = try_get_vcode(img)
            try:
                error = re.findall(
                    r'请修复以下错误<\/p><ul><li>(.*?)<',
                    self.post(self.BASE + '/login', data={
                        "LoginForm[username]": username,
                        "LoginForm[password]": password,
                        "LoginForm[verifyCode]": vcode,
                        "_csrf": vcv,
                        "login-button": ""
                    }).text
                )[0]
                if '验证码不正确' in error:
                    error = ''
                    continue
            except:
                pass
            if len(error) > 0:
                raise ConnectionError(error)
            break
