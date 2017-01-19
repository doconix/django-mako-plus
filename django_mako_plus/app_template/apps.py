## Not including the unicode_literals that Django's template does because DMP is Py3.0+.
from django.apps import AppConfig


class %(camel_case_app_name)sConfig(AppConfig):
    name = '%(app_name)s'
