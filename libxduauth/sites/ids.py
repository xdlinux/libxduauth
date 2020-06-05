from bs4 import BeautifulSoup
from requests import Session

from .._utils import parse_form_hidden_inputs


class IDSSession(Session):

    def __init__(
            self, target, username, password,
            *args, **kwargs
    ):
        super(IDSSession, self).__init__()
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
