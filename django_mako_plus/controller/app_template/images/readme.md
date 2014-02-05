Place images for this app in this directory.  

Reference images from your html pages with the following (where "appname" is the current app name):

        <img src="${ STATIC_URL }/appname/images/image.png" />

In your project's settings.py file, be sure you the following:

        STATIC_URL = '/static/'
        STATICFILES_DIRS = (
            BASE_DIR,  
        )
        STATIC_ROOT = os.path.join(BASE_DIR, 'static')  

During development, Django will use the `STATICFILES_DIRS` variable to find the files relative to your project root.

Before deployment, run `collectstatic` to collect your static files into a separate directory (called `/static/` in the settings above).  You should then point your web server (Apache, Nginx, IIS, etc.) to serve this folder directly to browsers.