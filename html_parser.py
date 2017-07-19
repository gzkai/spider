# encoding=utf-8

from bs4 import BeautifulSoup
import requests
import re
import conf

# visit the url and get page content
def get_page_content(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "movie.douban.com",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1"
    }

    # 登陆
    sess = requests.Session()
    log_data = {
        "source": "movie",
        "redir":"https://movie.douban.com/",
        "form_email": "310333037@qq.com",
        "form_password": "RfggfR123",
        "login":"登录"
    }
    rs = sess.post("https://accounts.douban.com/login", data=log_data)
    rsp = sess.get(url, headers=headers, params={"from":"subject-page"})

    html_content = rsp.content
    return html_content

# extract things you need and save it
def parser_html(html):
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", id="content")
    title = content.find("h1").span.string # 电影名
    info = content.find("div", id="info")
    info = str(info)
    info = re.sub(r"<.*?>", "", info).strip()
    for line in info.split("\n"):
        item = line.split(": ")
        print "%s----%s" % (item[0], item[1])

# find links you want to visit
def find_links(html, watching_list, watched_list):
    soup = BeautifulSoup(html, "lxml")
    links = soup.find_all("a")
    for link in links:
        url = link.get('href')
        if url is not None and check_url(url) and url not in watching_list and url not in watched_list:
            watching_list.append(url)

# check if the link is your need
def check_url(url):
    patter = re.compile(r"^((https|http)?://)movie.douban.com/subject/[1-9]\d*/\?from=subject-page.*")
    if patter.match(url) is None:
        return False
    else:
        return True

if __name__ == "__main__":
    parser_html(conf.html)