# Adding Platforms

While most of the app is cross-platform, the initial menu that users are presented with is OS-specific.  To add a new OS-specific menu, follow these steps:

1. In the `gui/platforms/` directory of the project, add a directory for the new platform.
2. Add your implementation code to this directory and make it exportable as a module.
    - Add any new dependencies to the `extras_require` section of `setup.py`, tagged with the proper platform.
    - Note that your code will be run in the main thread of the app.  All other code will run in separate threads.
3. Add a call to your main method to the `start_gui_across_platforms()` method in `gui/sb_gui.py`.
