from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Recipe(models.Model):
  title = models.CharField(max_length=50)
  description = models.CharField(max_length=120)
  ingredients = ArrayField( models.CharField(max_length=50, blank=True) )
  