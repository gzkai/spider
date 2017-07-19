# encoding=utf-8

import multiprocessing
import utils
import html_parser

watching_file = "watching.txt"
watched_file = "watched.txt"

def main():
    watching_list = utils.load_file(watching_file)
    watched_list = utils.load_file(watched_file)
    try:
        while len(watching_list) > 0:
            current_url = watching_list.pop(0)
            crawl_url(current_url, watching_list, watched_list)
        utils.save_file(watching_file, watching_list)
        utils.save_file(watched_file, watched_list)
    except:
        utils.save_file(watching_file, watching_list)
        utils.save_file(watched_file, watched_list)

def main_muti():
    watching_list = utils.load_file(watching_file)
    watched_list = utils.load_file(watched_file)
    pool = multiprocessing.Pool()
    try:
        while len(watching_list) > 0:
            current_url = watching_list.pop(0)
            pool.apply_async(crawl_url, (current_url, watching_list, watched_list,))
        pool.close()
        pool.join()
        utils.save_file(watching_file, watching_list)
        utils.save_file(watched_file, watched_list)
    except:
        pool.close()
        pool.join()
        utils.save_file(watching_file, watching_list)
        utils.save_file(watched_file, watched_list)

def crawl_url(url, watching_list, watched_list):
    print("parse url: %s, parsed %s" % (url, len(watched_list)))
    watched_list.append(url)
    html = html_parser.get_page_content(url)
    html_parser.parser_html(html)
    html_parser.find_links(html, watching_list, watched_list)


if __name__ == "__main__":
    main()