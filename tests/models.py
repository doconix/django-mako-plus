from django.db import models

# some models for testing

class IceCream(models.Model):
    name = models.TextField(null=True, blank=True)
    rating = models.IntegerField(default=0)