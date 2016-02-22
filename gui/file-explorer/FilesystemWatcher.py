import logging
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class SBFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, secretbox_instance):
        self.secretbox = secretbox_instance

    def on_moved(self, event):
        super(SBFileSystemEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(SBFileSystemEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(SBFileSystemEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(SBFileSystemEventHandler, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)


class FileWatcher():
    """
    An object used to de-register a filesystem watcher
    """
    def __init__(self, observer):
        self.observer = observer

    def stop(self):
        """
        De-registers the associated filesystem watcher and ends its thread.
        """
        self.observer.stop()
        self.observer.join()


def start_file_watcher(path, secretbox_instance):
    """
    Starts watching the filesystem for changes in a new thread and calls
    for corresponding actions in the SecretBox driver.
    This thread must be stopped after use.

    Args:
        path: the file path to recursively watch for changes on
        securebox_instance: the currently running instance of SecretBox

    Returns:
        A FileWatcher object to be stopped after use.
    """
    event_handler = SBFileSystemEventHandler(secretbox_instance)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return FileWatcher(observer)

