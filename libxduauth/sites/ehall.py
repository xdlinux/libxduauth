from .ids import IDSSession
from ..AuthSession import AuthSession


class EhallSession(IDSSession):
    cookie_name = 'ehall'

    def __init__(self, username, password, *args, **kwargs):
        AuthSession.__init__(self, f'{self.cookie_name}_{username}')
        if not self.is_logged_in():
            super().__init__(
                'http://ehall.xidian.edu.cn/login?service=http://ehall.xidian.edu.cn/new/index.html',
                username, password, *args, **kwargs
            )

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

    def is_logged_in(self):
        return self.get('http://ehall.xidian.edu.cn/jsonp/userFavoriteApps.json').json()['hasLogin']
