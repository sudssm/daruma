import argparse
import os
import urllib2

INTERNAL_SERVER_HOST = "localhost"
INTERNAL_SERVER_PORT = 28962


class status:
    QUEUED = 1
    COMPLETE = 2


def query_server(filename):
    prepend = os.path.expanduser("~/daruma")
    sanitized_filename = filename[len(prepend):].lstrip("/")
    response = urllib2.urlopen("http://" + INTERNAL_SERVER_HOST +
                               ":" + str(INTERNAL_SERVER_PORT) +
                               "/iconstatus/" + sanitized_filename)
    return response.read()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query file sync state.')
    parser.add_argument("filepath", help="The file path to be queried")
    args = parser.parse_args()

    try:
        file_status = query_server(args.filepath)
    except Exception as e:
        print e
    print file_status
