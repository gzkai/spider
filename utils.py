# encoding=utf-8


def load_file(filename):
    result = list()
    for line in open(filename):
        result.append(line.strip())
    return result

def save_file(filename, urls):
    with open(filename, "w") as f:
        for url in urls:
            f.write(url + "\n")