from django.db import models

# Example model definition
# ------------------------
class Example_Model(models.Model):
  name = models.CharField(max_length=30)
  date_created = models.DateTimeField(auto_add_now=True)

  

