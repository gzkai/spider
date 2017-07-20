# encoding=utf-8

from bs4 import BeautifulSoup
import requests
import re
import threading

file_lock = threading.Lock()

# visit the url and get page content
def get_page_content(url):
    # example: douban movie
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
    rsp = requests.get(url, headers=headers)

    html_content = rsp.content
    return html_content

# extract things you need and save it
def parser_html(html):
    # example: douban movie
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", id="content")
    title = content.find("h1").span.get_text() # 电影名
    info = content.find("div", id="info")
    info = info.get_text().strip()
    with open("movie.txt", "a") as movie_file:
    # 电影名,导演名,演员名,类型,制片国家/地区,语言,上映日期
        A = dict()
        for line in info.split("\n"):
            item = line.split(": ")
            A[item[0]] = item[1]
        line = u",".join([title or u"",
                         A.get(u"导演", u""),
                         A.get(u"主演", u""),
                         A.get(u"类型", u""),
                         A.get(u"制片国家/地区", u""),
                         A.get(u"语言", u""),
                         A.get(u"上映日期", u""),
                         A.get(u"片长", u"")])
        file_lock.acquire()
        movie_file.write(line.encode(encoding="utf-8") + "\n")
        file_lock.release()

# find links you want to visit
def find_links(html, watching_list, watched_list, lock):
    soup = BeautifulSoup(html, "lxml")
    links = soup.find_all("a")
    lock.acquire()
    for link in links:
        url = link.get('href')
        if url is not None and check_url(url) and url not in watching_list and url not in watched_list:
            watching_list.append(url)
    lock.release()

# check if the link is your need
def check_url(url):
    # example: douban movie
    patter = re.compile(r"^((https|http)?://)movie.douban.com/subject/[1-9]\d*/\?from=subject-page.*")
    if patter.match(url) is None:
        return False
    else:
        return True