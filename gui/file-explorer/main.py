import logging
import time
from watchdog.observers import Observer
from FilesystemWatcher import MyFileSystemEventHandler

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    path = '.'
    event_handler = MyFileSystemEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print "starting"
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
