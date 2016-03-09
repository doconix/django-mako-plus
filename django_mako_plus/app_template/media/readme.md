Place media files for this app in this directory: images, videos, PDF files, etc. -- any static files that aren't Javascript or CSS files.

Reference images from your html pages with the following (where "appname" is the current app name):

        <img src="${ STATIC_URL }appname/media/image.png" />

In your project's settings.py file, be sure you the following:

        STATIC_URL = '/static/'
        STATICFILES_DIRS = (
            BASE_DIR,  
        )
        STATIC_ROOT = os.path.join(BASE_DIR, 'static')  


# Deployment (Very Important)

At production/deployment, comment out `BASE_DIR` because it essentially makes your entire project available via your static url (a serious security concern).

        STATIC_URL = '/static/'
        STATICFILES_DIRS = (
        #    BASE_DIR,  
        )
        STATIC_ROOT = os.path.join(BASE_DIR, 'static')  

When you deploy to a web server, run `dmp_collectstatic` to collect your static files into a separate directory (called `/static/` in the settings above).  You should then point your web server (Apache, Nginx, IIS, etc.) to serve this folder directly to browsers.  

See the DMP tutorial for more information on static files.