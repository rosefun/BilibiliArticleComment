class Verify(object):
    def __init__(self, sessdata: str = None, csrf: str = None):
        self.sessdata = sessdata
        self.csrf = csrf

    def get_cookies(self):
        """
        获取cookies
        :return:
        """
        cookies = {}
        if self.has_sess():
            cookies["SESSDATA"] = self.sessdata
        if self.has_csrf():
            cookies["bili_jct"] = self.csrf
        return cookies

    def has_sess(self):
        """
        是否提供SESSDATA
        :return:
        """
        if self.sessdata is None:
            return False
        else:
            return True

    def has_csrf(self):
        """
        是否提供CSRF
        :return:
        """
        if self.csrf is None:
            return False
        else:
            return True

    def check(self):
        """
        检查权限情况
        -1: csrf 校验失败
        -2: SESSDATA值有误
        -3: 未提供SESSDATA
        :return:
        """
        ret = {
            "code": -2,
            "message": ""
        }
        if not self.has_sess():
            ret["code"] = -3
            ret["message"] = "未提供SESSDATA"
        else:
            api = "https://api.bilibili.com/x/web-interface/archive/like"
            data = {"bvid": "BV1uv411q7Mv", "like": 1, "csrf": self.csrf}
            req = requests.post(url=api, data=data, cookies=self.get_cookies())
            if req.ok:
                con = req.json()
                if con["code"] == -111:
                    ret["code"] = -1
                    ret["message"] = "csrf 校验失败"
                elif con["code"] == -101 or con["code"] == -400:
                    ret["code"] = -2
                    ret["message"] = "SESSDATA值有误"
                else:
                    ret["code"] = 0
                    ret["message"] = "0"
            else:
                raise exceptions.NetworkException(req.status_code)
        return ret