import hashlib
from datetime import datetime
from requests import Session

from ..utils.rsa import rsa_encrypt_by_pkcs1


class SportsSession(Session):
    BASE_URL = 'http://xd.5itsn.com//app/'

    __RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq4laolA7zAk7jzsqDb3O
a5pS/uCPlZfASK8Soh/NzEmry77QDZ2koyr96M5Wx+A9cxwewQMHzi8RoOfb3UcQ
O4UDQlMUImLuzUnfbk3TTppijSLH+PU88XQxcgYm2JTa546c7JdZSI6dBeXOJH20
quuxWyzgLk9jAlt3ytYygPQ7C6o6ZSmjcMgE3xgLaHGvixEVpOjL/pdVLzXhrMqW
VAnB/snMjpCqesDVTDe5c6OOmj2q5J8n+tzIXtnvrkxQSDaUp8DWF8meMwyTErmY
klMXzKic2rjdYZpHh4x98Fg0Q28sp6i2ZoWiGrJDKW29mntVQQiDNhKDawb4B45z
UwIDAQAB
-----END PUBLIC KEY-----"""

    __COMMON_HEADERS = {
        'channel': 'H5',
        'version': '99999',
        'type': '0'
    }
    __COMMON_SIGN_PARAMS = {
        'appId': '3685bc028aaf4e64ad6b5d2349d24ba8',
        'appSecret': 'e8167ef026cbc5e456ab837d9d6d9254'
    }

    user_id = ''

    def __get_sign(self, params):
        sorted_params = sorted(params.items())
        concated_params = '&'.join(
            ['{}={}'.format(entry[0], entry[1]) for entry in sorted_params])
        return hashlib.md5(concated_params.encode('utf-8')).hexdigest()

    def __append_payload_sign(self, payload):
        timestamp = int(datetime.now().timestamp() * 1000)
        payload['timestamp'] = timestamp
        sign_params = payload.copy()
        sign_params.update(self.__COMMON_SIGN_PARAMS)
        payload['sign'] = self.__get_sign(sign_params)

    def post(self, url, data):
        payload = data.copy()
        self.__append_payload_sign(payload)

        return super().post(url, data=payload, headers=self.__COMMON_HEADERS)

    def __init__(self, username, password, *args, **kwargs):
        super(SportsSession, self).__init__(*args, **kwargs)
        login_response = self.post(
            self.BASE_URL + 'h5/login', data={
                'uname': username,
                'pwd': rsa_encrypt_by_pkcs1(self.__RSA_PUBLIC_KEY, password)
            }).json()
        if login_response['returnCode'] != '200':
            raise ConnectionError('登录失败: ' + login_response['returnMsg'])

        self.user_id = login_response['data']['id']
        self.headers.update({
            'token': login_response['data']['token']
        })
