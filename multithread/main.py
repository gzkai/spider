# encoding=utf-8

import sys
sys.path.append("../")

import logging
import html_parser
import utils
import threading
import time

watching_file = "../watching.txt"
watched_file = "../watched.txt"
watching = utils.load_file(watching_file)
watched = utils.load_file(watched_file)
lock = threading.Lock()

def main():
    global lock
    global watching
    global watched
    sleep_count = 0
    try:
        while True:
            if len(watching) > 0:
                lock.acquire()
                current_url = watching.pop(0)
                lock.release()
                crawl_url(current_url, watching, watched)
            else:
                sleep_count += 1
                if sleep_count > 3:
                    break
                time.sleep(5)
        update_file()
    except KeyboardInterrupt as e:
        update_file()
        logging.exception(e)
    except Exception as e:
        update_file()
        logging.exception(e)

def crawl_url(url, watching_list, watched_list):
    global lock
    print("visiting url: %s, visited %s links, waiting %s" % (url, len(watched_list), len(watching_list)))
    html = html_parser.get_page_content(url)
    html_parser.parser_html(html)
    lock.acquire()
    watched_list.append(url)
    lock.release()
    html_parser.find_links(html, watching_list, watched_list, lock)
    update_file()

def update_file():
    global watching
    global watched
    global lock
    lock.acquire()
    utils.save_file(watching_file, watching)
    utils.save_file(watched_file, watched)
    lock.release()

if __name__ == "__main__":
    num_thread = 4
    for _ in range(num_thread):
        t = threading.Thread(target=main)
        t.start()