from bs4 import BeautifulSoup

from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs


class IDSSession(AuthSession):

    def __init__(
            self, target, username, password,
            *args, **kwargs
    ):
        super(IDSSession, self).__init__('ids')
        self.headers.update({'User-Agent': 'Mobile'})
        page = self.get(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target}
        ).text
        params = parse_form_hidden_inputs(BeautifulSoup(page, "lxml"))
        self.post(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target},
            data=dict(params, **{
                'username': username,
                'password': password
            })
        )
