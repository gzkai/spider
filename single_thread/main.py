# encoding=utf-8

import logging

import html_parser
import utils

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
    except KeyboardInterrupt as e:
        utils.save_file(watching_file, watching_list)
        utils.save_file(watched_file, watched_list)
        logging.exception(e)
    except Exception as e:
        utils.save_file(watching_file, watching_list)
        utils.save_file(watched_file, watched_list)
        logging.exception(e)

def crawl_url(url, watching_list, watched_list):
    print("visiting url: %s, visited %s links, waiting %s" % (url, len(watched_list), len(watching_list)))
    html = html_parser.get_page_content(url)
    html_parser.parser_html(html)
    watched_list.append(url)
    html_parser.find_links(html, watching_list, watched_list)
    utils.save_file(watching_file, watching_list)
    utils.save_file(watched_file, watched_list)

if __name__ == "__main__":
    main()