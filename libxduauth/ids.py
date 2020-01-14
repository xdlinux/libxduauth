from requests import Session
import re


class IDSSession(Session):
    REGEX_HIDDEN_TAG = '<input type="hidden" name="(.*)" value="(.*)"'
    REGEX_HTML_COMMENT = r'<!--\s*([\s\S]*?)\s*-->'

    def __init__(
        self, target, username, password,
        *args, **kwargs
    ):
        super(IDSSession, self).__init__(*args, **kwargs)
        page = self.get(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target}
        ).text
        page = re.sub(self.REGEX_HTML_COMMENT, '', page)
        params = {i[0]: i[1] for i in re.findall(self.REGEX_HIDDEN_TAG, page)}
        self.post(
            'http://ids.xidian.edu.cn/authserver/login',
            params={'service': target},
            data=dict(params, **{
                'username': username,
                'password': password
            })
        )

    