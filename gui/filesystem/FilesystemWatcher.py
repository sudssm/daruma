import os
from contextlib import contextmanager
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from custom_exceptions import exceptions


class DarumaFileSystemEventHandler(PatternMatchingEventHandler):
    """
    An internal class to handle events from the filesystem.
    """

    def __init__(self, path, app_state):
        self.path = path
        self.app_state = app_state
        super(DarumaFileSystemEventHandler, self).__init__(ignore_patterns=[path, "*/.DS_Store"])

    @contextmanager
    def get_safe_daruma(self):
        try:
            yield self.app_state.daruma
        except AttributeError:
            # daruma was None due to not being initialized yet
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
        super(DarumaFileSystemEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        print "Moved", what, "from", event.src_path, "to", event.dest_path

        with self.get_safe_daruma() as daruma:
            if event.is_directory:
                # If we get a move event on a directory from watchdog, then the
                # directory is already empty, since watchdog notifies us of all
                # the children first.
                daruma.mk_dir(self.sanitize(event.dest_path))
                daruma.delete(self.sanitize(event.src_path))
            else:
                daruma.move(self.sanitize(event.src_path),
                            self.sanitize(event.dest_path))

    def on_created(self, event):
        super(DarumaFileSystemEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        print "Created", what, ":", event.src_path

        with self.get_safe_daruma() as daruma:
            if event.is_directory:
                daruma.mk_dir(self.sanitize(event.src_path))
            else:
                with open(event.src_path) as src_file:
                    daruma.put(self.sanitize(event.src_path),
                               src_file.read())

    def on_deleted(self, event):
        super(DarumaFileSystemEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        print "Deleted", what, ":", event.src_path

        with self.get_safe_daruma() as daruma:
            daruma.delete(self.sanitize(event.src_path))

    def on_modified(self, event):
        super(DarumaFileSystemEventHandler, self).on_modified(event)

        print "Modified", event.src_path
        with self.get_safe_daruma() as daruma:
            if not event.is_directory:
                with open(event.src_path) as src_file:
                    daruma.put(self.sanitize(event.src_path),
                               src_file.read())


class FilesystemWatcher():
    """
    A class representing the thread used to monitor the filesystem for changes
    and call for the corresponding actions in the daruma driver.
    This thread must be stopped after use by calling the object's stop method.
    """

    def __init__(self, path, app_state):
        """
        Args:
            path: the file path to recursively watch for changes on.
            app_state: the currently ApplicationState instance.
        """
        event_handler = DarumaFileSystemEventHandler(path, app_state)
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)

    def start(self):
        """
        Starts running the observer in the given thread.
        """
        self.observer.start()

    def stop(self):
        """
        De-registers the filesystem watcher and ends the thread.
        """
        self.observer.stop()
        self.observer.join()
