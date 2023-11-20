from django.db import models
from django.contrib.postgres.fields import ArrayField
from enums import choices

# Create your models here.


class Tag(models.Model):
  name = models.CharField(max_length=20)

  class Meta:
    ordering = ("name", )

  def __str__(self) -> str:
    return self.name

class Recipe(models.Model):
  title             = models.CharField(max_length=50)
  description       = models.CharField(max_length=200)
  ingredients       = ArrayField( models.JSONField() )
  instructions      = ArrayField( models.CharField(max_length=250) )
  preparation_time  = models.TimeField()
  cooking_time      = models.TimeField()
  servings          = models.IntegerField()
  images            = ArrayField( models.URLField(max_length=500, blank=True, null=True), size=4 )
  tags              = models.ManyToManyField(Tag)
  nutritional_value = models.JSONField(default=dict)
  chef              = models.JSONField()
  status            = models.CharField(max_length=10, choices=choices.RECIPE_STATUS_CHOICES, default="DRAFT")
  created           = models.DateTimeField(auto_now_add=True)
  published         = models.DateTimeField(auto_now=True)


  def __str__(self) -> str:
    return self.title
  
  def tag_names(self):
    return ', '.join([tag.name for tag in self.tags.all()])
  tag_names.short_description = "Tag Names"
  