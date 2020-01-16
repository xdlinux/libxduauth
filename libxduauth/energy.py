from requests import Session


class EnergySession(Session):
    BASE = 'http://10.168.55.50:8088'

    def __init__(self, username, password):
        self.get(self.BASE+"/searchWap/Login.aspx")
        self.post(
            self.BASE+"/ajaxpro/SearchWap_Login,App_Web_fghipt60.ashx",
            data={
                "webName": username,
                "webPass": password
            }, headers={
                "AjaxPro-Method": "getLoginInput",
                'Origin': self.BASE
            }
        )
