import time
from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs
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
            params={'service': target}
        ).text
	is_need_captcha = self.get(
            'https://ids.xidian.edu.cn/authserver/checkNeedCaptcha.htl',
            params={'username': username, '_': int(time.time() * 1000)}
        ).json()['isNeed']
	if is_need_captcha:
            captcha = self.get(
                'https://ids.xidian.edu.cn/authserver/common/openSliderCaptcha.htl',
                params={'_': str(int(time.time() * 1000))}
            )
            # 返回: {
            #     'bigImage': ..., # 背景图(base64)
            #     'smallImage': ..., # 滑块图(base64)
            #     'tagWidth": 93, # 无用, 恒93
            #     'yHeight': 0 # 无用, 恒0
            # }
            img = Image.open(BytesIO(captcha.json()['bigImage']))
            img.show()
            # move_len: 背景图左侧到滑块目标位置左侧的宽度
            move_len = input('滑块位移:')
            # canvasLength: canvas宽度, 硬编码280
            # moveLength: 按比例缩放后的滑块位移, 有容错
            verify = self.post(
                'https://ids.xidian.edu.cn/authserver/common/verifySliderCaptcha.htl',
                data={
                      'canvasLength': '280',
                      'moveLength': str(move_len * 280 // img.width)
                }
            )
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
