Translation (Internationalization)
----------------------------------

If your site needs to be translated into other languages, this section is for you. I'm sure you are aware that Django has full support for translation to other languages. If not, you should first read the standard Translation documentation at http://docs.djangoproject.com/en/dev/topics/i18n/translation/.

DMP supports Django's translation functions--with one caveat. Since Django doesn't know about Mako, it can't translate strings in your Mako files. DMP fixes this with the ``dmp_makemessages`` command. Instead of running ``python3 manage.py makemessages`` like the Django tutorial shows, run ``python3 manage.py dmp_makemessages``. Since the DMP version is an extension of the standard version, the same command line options apply to both.

    IMPORTANT: Django ignores hidden directories when creating a
    translation file. Most DMP users keep compiled templates in the
    hidden directory ``.cached_templates``. The directory is hidden on
    Unix because it starts with a period. If your cached templates are
    in hidden directories, be sure to run the command with
    ``--no-default-ignore``, which allows hidden directories to be
    searched.

    Internally, ``dmp_makemessages`` literally extends the
    ``makemessages`` class. Since Mako templates are compiled into .py
    files at runtime (which makes them discoverable by
    ``makemessages``), the DMP version of the command simply finds all
    your templates, compiles them, and calls the standard command.
    Django finds your translatable strings within the cached\_templates
    directory (which holds the compiled Mako templates).

Suppose you have a template with a header you want translated. Simply use the following in your template:

.. code:: html

    <%! from django.utils.translation import ugettext as _ %>
    <p>${ _("World History") }</p>

Run the following at the command line:

::

    python3 manage.py dmp_makemessages --no-default-ignore

Assuming you have translations set up the way Django's documentation tells you to, you'll get a new language.po file. Edit this file and add the translation. Then compile your translations:

::

    python3 manage.py compilemessages

Your translation file (language.mo) is now ready, and assuming you've set the language in your session, you'll now see the translations in your template.

    FYI, the ``dmp_makemessages`` command does everything the regular
    command does, so it will also find translatable strings in your
    regular view files as well. You don't need to run both
    ``dmp_makemessages`` and ``makemessages``
