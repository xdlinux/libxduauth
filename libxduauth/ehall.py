from .ids import IDSSession
import re


class EhallSession(IDSSession):
    def __init__(self, username, password, *args, **kwargs):
        super().__init__(
            'http://ehall.xidian.edu.cn:80//appShow',
            username, password, *args, **kwargs
        )
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
        })

    def use_app(self, app_id):
        self.get('http://ehall.xidian.edu.cn//appShow', params={
            'appId': app_id
        }, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        })

    def get_app_list(self, search_key=''):
        app_list = self.get('http://ehall.xidian.edu.cn/jsonp/serviceSearchCustom.json', params={
            'searchKey': search_key,
            'pageNumber': 1,
            'pageSize': 150,
            'sortKey': 'recentUseCount',
            'orderKey': 'desc'
        }).json()
        assert app_list['hasLogin']
        return app_list['data']

    def get_app_id(self, search_key):
        search_result = self.get_app_list(search_key)
        if len(search_result) == 0:
            return None
        if len(search_result) > 1:
            # warn('multiple results found, returning the first one')
            pass
        return search_result[0]['appId']
