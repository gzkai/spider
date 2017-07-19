# encoding=utf-8

import multiprocessing


def load_file(filename):
    result = multiprocessing.Manager().list()
    for line in open(filename):
        result.append(line.strip())
    return result

def save_file(filename, urls):
    with open(filename, "w") as f:
        for url in urls:
            f.write(url + "\n")