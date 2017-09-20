# coding=utf-8
import requests
import base64
import re
import urllib
import rsa
import json
import binascii
from bs4 import BeautifulSoup
import logging

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'}

class Account:
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd
        self.url_prelogin = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_=1505628682426"
        self.url_login = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)"
        self.sess = None
        self.uid = None

    def __pre_login(self):
        rsp = self.sess.get(self.url_prelogin)
        data = re.findall(r"(?<=\().*(?=\))", rsp.text)[0]
        data = json.loads(data)
        servertime = data[u'servertime']
        nonce = data[u'nonce']
        pubkey = data[u'pubkey']
        rsakv = data[u'rsakv']
        return servertime, nonce, pubkey, rsakv

    def login(self):
        """
        登录
        :return:
        """
        self.sess = requests.Session()
        servertime, nonce, pubkey, rsakv = self.__pre_login()
        su = base64.b64encode(urllib.quote(self.username))
        key = rsa.PublicKey(int(pubkey, 16), 65537)
        message = str(servertime) + "\t" + str(nonce) + "\n" + str(self.passwd)
        sp = binascii.b2a_hex(rsa.encrypt(message, key))
        post_data = {
            "entry":"weibo",
            "gateway":"1",
            "from":"",
            "savestate":"7",
            "useticket":"1",
            'ssosimplelogin': "1",
            "pagerefer":"",
            "vsnf":"1",
            'vsnval': "",
            "su":su,
            "service":"miniblog",
            "servertime":servertime,
            "nonce":nonce,
            "pwencode":"rsa2",
            "rsakv":rsakv,
            "sp":sp,
            "encoding":"UTF-8",
            "url":"http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype":"META"
        }
        # header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'}
        rsp = self.sess.post(self.url_login, data=post_data, headers=header)
        login_url = urllib.unquote(re.findall(r'location\.replace\([\'"](.*?)[\'"]\)', rsp.text)[0])
        login_url = re.findall(r"http://weibo.*retcode=0", login_url)[0]
        rsp = self.sess.get(login_url)
        self.uid = re.findall(r'"uniqueid":"(\d+)",', rsp.text)[0]
        print("登录成功...")
        return self

    def __get_more(self, params):
        """
        点击展开全文链接
        :param params:
        :return:
        """
        url = "http://s.weibo.com/ajax/direct/morethan140?%s" % params
        rsp = self.sess.get(url, headers=header)
        data = json.loads(rsp.text)
        return data["data"]["html"]

    def find_weibo(self, html):
        """
        从html中提取微博相关内容
        :param html:
        :return:
        """
        if self.sess is None:
            self.login()
        soup = BeautifulSoup(html, "lxml")
        div_weibos = soup.find_all("div", class_="WB_cardwrap S_bg2 clearfix")
        weibos = []
        for ddd in div_weibos:
            try:
                div_weibo = ddd.find("div", attrs={"action-type": "feed_list_item"})
                # since_id
                since_id = div_weibo["mid"]
                # weibo_time
                div_time = div_weibo.find("div", class_="feed_from W_textb")
                weibo_time = div_time.a["title"]
                #
                div_main = div_weibo.find("div", class_="feed_content wbcon")
                # author
                author = div_main.find("a", class_="W_texta W_fb")["nick-name"]
                # verified_type
                verified_type = ""
                a_type = div_main.find("a", class_="W_icon icon_approve")
                if a_type: verified_type = a_type["title"]
                # content
                content = div_weibo.find("p", class_="comment_txt")
                more = content.find("a", class_="WB_text_opt")
                if more is not None:
                    content = self.__get_more(more["action-data"])
                else:
                    content = str(content)
                content = re.sub(r"<.*?>", "", content).strip()
                # 评论、转发、点赞
                comment_count = 0
                repost_count = 0
                attitudes_count = 0
                div_cra = div_weibo.find("div", class_="feed_action clearfix")
                span_cra = div_cra.find_all("span", class_="line S_line1")
                if span_cra[2].em and span_cra[2].em.string:
                    comment_count = int(span_cra[2].em.string)
                if span_cra[1].em and span_cra[1].em.string:
                    repost_count = int(span_cra[1].em.string)
                if span_cra[3].em and span_cra[3].em.string:
                    attitudes_count = int(span_cra[3].em.string)
                #
                weibo = Weibo(since_id, content, author, weibo_time)
                weibo.comment_count = comment_count
                weibo.repost_count = repost_count
                weibo.attitudes_count = attitudes_count
                weibo.verified_type = verified_type
                weibos.append(weibo)
            except Exception as e:
                logging.warning("Exception in %s: %s" % (self.find_weibo, e))
        return weibos

    def keyword_search(self, keyword, page_num):
        if page_num > 50 or page_num < 0:
            raise ValueError("必须是 [1,50] 页...")
        if self.sess is None:
            self.login()
        search_url = "http://s.weibo.com/weibo/%s&page=%s" % (keyword, page_num)
        rsp = self.sess.get(search_url)
        # 提取微博内容
        json_datas = re.findall(r"<script>STK && STK\.pageletM && STK\.pageletM\.view\((.*?)\)</script>", rsp.text)
        json_data = None
        for d in json_datas:
            if '"pid":"pl_weibo_direct"' in d:
                json_data = d
                break
        html = json.loads(json_data)["html"]
        return self.find_weibo(html)


class Weibo:
    def __init__(self, since_id, content, author, weibo_time):
        self.since_id = since_id
        self.content = content
        self.author = author
        self.weibo_time = weibo_time
        self.comment_count = 0
        self.repost_count = 0
        self.attitudes_count = 0
        self.verified_type = ""

    def __str__(self):
        return self.since_id