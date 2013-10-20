from django.db import models
from django.contrib import admin
from .models import *

# register any models here
admin.site.register(Calculation)
