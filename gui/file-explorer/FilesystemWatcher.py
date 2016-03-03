import logging
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class SBFileSystemEventHandler(FileSystemEventHandler):
    """
    An internal class to handle events from the filesystem.
    """

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



class FilesystemWatcher():
    """
    A class representing the thread used to monitor the filesystem for changes
    and call for the corresponding actions in the SecretBox driver.
    This thread must be stopped after use by calling the object's stop method.
    """

    def __init__(self, path, secretbox_instance):
        """
        Args:
            path: the file path to recursively watch for changes on.
            securebox_instance: the currently running instance of SecretBox.
        """
        event_handler = SBFileSystemEventHandler(secretbox_instance)
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()

    def stop(self):
        """
        De-registers the filesystem watcher and ends the thread.
        """
        self.observer.stop()
        self.observer.join()

