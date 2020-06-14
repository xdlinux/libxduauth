import hashlib
import json
import random
import time

from requests import Session


def _generate_uuid():
    a = [str(random.random())[2:10] for i in range(2)]
    a = [a[i] + str(int(time.time() * 1000))[-10:] for i in range(2)]
    a = [hex(int(a[i]))[2:10] for i in range(2)]
    return "web" + a[0] + a[1]


class WXSession(Session):
    BASE = 'http://202.117.121.7:8080/'

    def _dump_sign(self, data):
        l = list(data.keys())
        l.sort()
        s = ''
        for i in l:
            s += i + '=' + str(data[i]) + '&'
        s = s[:-1]
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def options(self, url):
        return super().options(url, headers={
            'Access-Control-Request-Headers': 'content-type,token',
            'Access-Control-Request-Method': 'POST'
        })

    def post(self, url, data=None, json=None, headers=None, param=None):
        self.options(url)
        if param is not None:
            json = {
                'appKey': "GiITvn",
                'param': param,
                'secure': 0
            }
        if json is not None:
            json['time'] = int(time.time() * 1000)  # 先后顺序
            json['sign'] = self._dump_sign(json)  # 数据签名在生成时间戳之后
            if headers == None:
                headers = {}
            headers = dict(headers, **{
                'Content-Type': 'application/json;charset=UTF-8'
            })
        return super().post(url, json=json, data=data, headers=headers)

    def __init__(self, username, password, *args, **kwargs):
        super(WXSession, self).__init__(*args, **kwargs)
        data = {
            'appKey': "GiITvn",
            'param': json.dumps({
                'userName': username,
                'password': password,
                'schoolId': 190,
                'uuId': _generate_uuid()
            }),
            'secure': 0
        }
        result = self.post(self.BASE + 'baseCampus/login/login.do', json=data).json()
        if result['isConfirm'] != 1:
            raise ConnectionError('登录失败')  # 请检查credentials.py
        self.headers.update({
            'token': result['token'][0] + '_' + result['token'][1]
        })
