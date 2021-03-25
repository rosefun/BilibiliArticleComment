# coding:utf-8
import sys,os
os.chdir(r"F:\研究生\github项目\自动获取Bilibili评论")
sys.path.append(r"F:\研究生\github项目\自动获取Bilibili评论")

import copy
import exceptions
import json
import utils
import re
import requests

COMMENT_TYPE_MAP = {
    "video": 1,
    "article": 12,
    "dynamic_draw": 11,
    "dynamic_text": 17,
    "audio": 14,
    "audio_list": 19
}

COMMENT_SORT_MAP = {
    "like": 2,
    "time": 0
}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bilibili.com/"
}

request_settings = {
    "use_https": True,
    "proxies": None
}


def send_request(method: str, url: str, params=None, data=None, cookies=None, headers=None, data_type: str = "form", **kwargs):
    if params is None:
        params = {}
    if data is None:
        data = {}
    if cookies is None:
        cookies = {}
    if headers is None:
        headers = copy.deepcopy(DEFAULT_HEADERS)
    if data_type.lower() == "json":
        headers['Content-Type'] = "application/json"
    st = {
        "url": url,
        "params": params,
        "headers": headers,
        "verify": request_settings["use_https"],
        "data": data,
        "proxies": request_settings["proxies"],
        "cookies": cookies
    }
    st.update(kwargs)

    req = requests.request(method, **st)
    if req.ok:
        content = req.content.decode("utf8")
        if req.headers.get("content-length") == 0:
            return None
        if 'jsonp' in params and 'callback' in params:
            con = json.loads(re.match(".*?({.*}).*", content, re.S).group(1))
        else:
            con = json.loads(content)
        if con["code"] != 0:
            if "message" in con:
                msg = con["message"]
            elif "msg" in con:
                msg = con["msg"]
            else:
                msg = "请求失败，服务器未返回失败原因"
            raise exceptions.BilibiliException(con["code"], msg)
        else:
            if 'data' in con.keys():
                return con['data']
            else:
                if 'result' in con.keys():
                    return con["result"]
                else:
                    return None
    else:
        raise exceptions.NetworkException(req.status_code)
        
def get_response(url, params=None, cookies=None, headers=None, data_type: str = "form", **kwargs):
    """
    专用GET请求
    :param data_type:
    :param url:
    :param params:
    :param cookies:
    :param headers:
    :param kwargs:
    :return:
    """
    resp = send_request("GET", url=url, params=params, cookies=cookies, headers=headers, data_type=data_type, **kwargs)
    return resp

def get_comments_raw(oid: int, type_: str, order: str = "time", pn: int = 1, verify: utils.Verify = None):
    """
    通用获取评论
    :param oid:
    :param type_:
    :param order:
    :param pn:
    :param verify:
    :return:
    """
    if verify is None:
        verify = utils.Verify()

    type_ = COMMENT_TYPE_MAP.get(type_, None)
    assert type_ is not None, exceptions.BilibiliApiException("不支持的评论类型")

    order = COMMENT_SORT_MAP.get(order, None)
    assert order is not None, exceptions.BilibiliApiException("不支持的排序方式，支持：time（时间倒序），like（热度倒序）")
    # 参数检查完毕
    params = {
        "oid": oid,
        "type": type_,
        "sort": order,
        "pn": pn
    }
    #comment_api = API["common"]["comment"]
    #api = comment_api.get("get", None)
    api  = {}
    api["url"] = "https://api.bilibili.com/x/v2/reply"
    resp = get_response(api["url"], params=params, cookies=verify.get_cookies())
    return resp


def get_comments(oid: int, type_: str, order: str = "time", verify: utils.Verify = None):
    """
    通用循环获取评论，使用生成器语法
    :param type_:
    :param order:
    :param oid:
    :param verify:
    :return:
    """
    if verify is None:
        verify = utils.Verify()

    page = 1
    while True:
        resp = get_comments_raw(oid=oid, pn=page, order=order, verify=verify, type_=type_)
        if "replies" not in resp:
            break
        if resp["replies"] is None:
            break
        for rep in resp["replies"]:
            yield rep
        page += 1

def get_comments_g(cv: int, order: str = "time", verify: utils.Verify = None):
    """
    获取评论
    :param cv: cv号
    :param order:
    :param verify:
    :return:
    """
    replies = get_comments(cv, "article", order, verify)
    return replies
    
def main():
    replies = get_comments_g(10434250)
    print(replies)
    
    comments = []
    for comment in replies:
        # 将评论项目加入列表，也就是普通的所有评论爬虫
        comments.append(comment["content"]["message"])
    print(comments)
    return
    
if __name__ == "__main__":
    main()
    
    
    