# encoding=utf-8

from bs4 import BeautifulSoup
import requests
import re

# visit the url and get page content
def get_page_content(url):
    rsp = requests.get(url)
    html_content = rsp.content
    return html_content

# extract things you need and save it
def parser_html(html):
    # example douban movie
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
    # example douban movie
    patter = re.compile(r"^((https|http)?://)movie.douban.com/subject/[1-9]\d*/\?from=subject-page.*")
    if patter.match(url) is None:
        return False
    else:
        return True