import os
from contextlib import contextmanager
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from custom_exceptions import exceptions


class SBFileSystemEventHandler(PatternMatchingEventHandler):
    """
    An internal class to handle events from the filesystem.
    """

    def __init__(self, path, app_state):
        self.path = path
        self.app_state = app_state
        super(SBFileSystemEventHandler, self).__init__(ignore_patterns=[path, "*/.DS_Store"])

    @contextmanager
    def get_safe_secretbox(self):
        try:
            yield self.app_state.secretbox
        except AttributeError:
            # SecretBox was None due to not being initialized yet
            pass
        except exceptions.FatalOperationFailure:
            # TODO
            print "fatal operation failure"
        except exceptions.ReadOnlyMode:
            # TODO
            print "read only mode"
        except exceptions.InvalidPath:
            # TODO
            print "invalid path"
        except exceptions.FileNotFound:
            # TODO
            print "file not found"

    def sanitize(self, path):
        """
        Returns the path name without the components leading up to the search
        folder.
        """
        return os.path.relpath(path, self.path)

    def on_moved(self, event):
        super(SBFileSystemEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        print "Moved", what, "from", event.src_path, "to", event.dest_path

        with self.get_safe_secretbox() as secretbox:
            if event.is_directory:
                # If we get a move event on a directory from watchdog, then the
                # directory is already empty, since watchdog notifies us of all
                # the children first.
                secretbox.mk_dir(self.sanitize(event.dest_path))
                secretbox.delete(self.sanitize(event.src_path))
            else:
                secretbox.move(self.sanitize(event.src_path),
                               self.sanitize(event.dest_path))

    def on_created(self, event):
        super(SBFileSystemEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        print "Created", what, ":", event.src_path

        with self.get_safe_secretbox() as secretbox:
            if event.is_directory:
                secretbox.mk_dir(self.sanitize(event.src_path))
            else:
                with open(event.src_path) as src_file:
                    secretbox.put(self.sanitize(event.src_path),
                                  src_file.read())

    def on_deleted(self, event):
        super(SBFileSystemEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        print "Deleted", what, ":", event.src_path

        with self.get_safe_secretbox() as secretbox:
            secretbox.delete(self.sanitize(event.src_path))

    def on_modified(self, event):
        super(SBFileSystemEventHandler, self).on_modified(event)

        print "Modified", event.src_path
        with self.get_safe_secretbox() as secretbox:
            if not event.is_directory:
                with open(event.src_path) as src_file:
                    secretbox.put(self.sanitize(event.src_path),
                                  src_file.read())


class FilesystemWatcher():
    """
    A class representing the thread used to monitor the filesystem for changes
    and call for the corresponding actions in the SecretBox driver.
    This thread must be stopped after use by calling the object's stop method.
    """

    def __init__(self, path, app_state):
        """
        Args:
            path: the file path to recursively watch for changes on.
            app_state: the currently ApplicationState instance.
        """
        event_handler = SBFileSystemEventHandler(path, app_state)
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()

    def stop(self):
        """
        De-registers the filesystem watcher and ends the thread.
        """
        self.observer.stop()
        self.observer.join()
