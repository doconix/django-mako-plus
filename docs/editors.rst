Editors
==========================

This page contains ideas for customizing your favorite editor for DMP and Django development. If your editor isn't listed here, please contribute ideas for it!

:File extensions:
    Templates can have any extension--DMP does not require ``.html`` extensions to your files. For example, if you prefer ``*.mako``, simply use this extension in view functions:

    .. code-block:: python

        @view_function
        def process_request(request):
            ...
            return request.dmp.render('mypage.mako', {...})


VSCode
-------------------------------------

:Code Highlighting:
    A vscode extension for Mako exists in the marketplace. Simply search "Mako" on the extensions tab and install.

    To activate highlighting, click the language in the bottom right of the vscode window (or type "Change Language Mode" in the command dropdown) and select Mako.

    If you want to make the association stick, add the following to the vscode settings file [Command Palette: Open settings (JSON)]:

    ::

        "files.associations": {
            "*.htm": "mako",
            "*.html": "mako"
        }


Atom
----------------------

:Code Highlighting:
    An Atom package for Mako can be downloaded from within the editor. Open Settings and search for "Mako" on the Install tab. Install the ``language-mako`` package. Once installed, click on it if you want to customize its settings.

    To activate highlighting, click the language in the bottom right of the atom window and select ``HTML (Mako)``.

    If you want to make the association stick, open the Atom ``config.cson`` and add the following:

    ::

        "*":
            core:
                customFileTypes:
                'text.html.mako': [
                    'html',
                    'htm'
                ]
