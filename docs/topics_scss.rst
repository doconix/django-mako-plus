Sass Integration
========================

Yeah, I know, you could just run the SASS file watcher.  Or you could install that plugin for your editor that autocompiles .scss files when you hit Ctrl-S.  But if you want to use it, DMP can compile the auto-linked style files.  This feature is disabled by default.

When enabled, DMP will compile your .scss files before sending the generated CSS to the browser. When a template is rendered the first time, DMP checks the timestamps on the .scss file and .css file, and it reruns Sass when necessary. Just be sure to set the ``SCSS_BINARY`` option in settings.py.

When ``DEBUG = True``, DMP checks the timestamps every time a template is rendered. When in production mode (``DEBUG = False``), DMP only checks the timestamps the
first time a template is rendered -- you'll have to restart your server to recompile updated .scss files. You can disable Sass integration by removing the
``SCSS_BINARY`` from the settings or by setting it to ``None``.

Note that ``SCSS_BINARY`` *must be specified in a list*. DMP uses Python's subprocess.Popen command without the shell option (it's more cross-platform that way, and it
works better with spaces in your paths). Specify any arguments in the list as well. For example, the following settings are all valid:

::

    'SCSS_BINARY': [ 'scss' ],
    # or:
    'SCSS_BINARY': [ 'C:\\Ruby200-x64\\bin\\scss' ],
    # or:
    'SCSS_BINARY': [ '/usr/bin/env', 'scss', '--unix-newlines', '--cache-location', '/tmp/' ],
    # or, to disable:
    'SCSS_BINARY': None,

If Sass isn't running right, check the DMP log statements. When the log is enabled, it shows the exact command syntax that DMP is using. Copy and paste the code into a terminal and troubleshoot the command manually.

    You might be wondering if DMP supports ``.scssm`` files (Mako embedded in Sass files). Through a bit of hacking the process, it's a qualified Yes!

    Consider ``.scssm`` support in beta status.  Even if it was working perfectly, it's a *franken-mako* that should probably be avoided anyway. But the supported things work do work, which more plainly stated, means Mako expressions work: ``${ ... }``. Any other Mako constructs get stripped out by the compiler.
