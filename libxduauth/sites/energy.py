from requests import Session


class EnergySession(Session):
    BASE = 'http://10.168.55.50:8088'

    def __init__(self, username, password, *args, **kwargs):
        super(EnergySession, self).__init__(*args, **kwargs)
        self.get(self.BASE + "/searchWap/Login.aspx")
        self.post(
            self.BASE + "/ajaxpro/SearchWap_Login,App_Web_fghipt60.ashx",
            json={
                "webName": username,
                "webPass": password
            }, headers={
                "AjaxPro-Method": "getLoginInput",
                'Origin': self.BASE
            }
        )
