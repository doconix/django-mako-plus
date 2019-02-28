.. _deploy_recommendations:

Deployment Recommendations
==========================

This section has nothing to do with the Django-Mako-Framework, but I want to address a couple issues in hopes that it will save you some headaches. One of the most difficult decisions in Django development is deciding how to deploy your system. In particular, there are several ways to connect Django to your web server: mod\_wsgi, FastCGI, etc.

At MyEducator, we've been through all of them at various levels of testing and production. By far, we've had the best success with `uWSGI <http://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/>`__. It is a professional server, and it is stable.

One other decision you'll have to make is which database use. I'm excluding the "big and beefies" like Oracle or DB2. Those with sites that need these databases already know who they are. Most of you will be choosing between MySQL, PostgreSQL, and perhaps another mid-level database.

In choosing databases, you'll find that many, if not most, of the Django developers use PostgreSQL. The system is likely tested best and first on PG. We started on MySQL, and we moved to PG after experiencing a few problems. Since deploying on PG, things have been amazingly smooth.

Your mileage may vary with everything in this section. Do your own testing and take it all as advice only. Best of luck.
