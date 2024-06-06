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


class Chef(models.Model):
  username      = models.CharField(max_length=100, db_index=True)
  first_name    = models.CharField(max_length=20, default='')
  last_name     = models.CharField(max_length=20, default='')
  vote_strength = models.IntegerField(default=1) # this attr determines the number of vote the user gives at a single click when voting for a recipe
  is_verified   = models.BooleanField(default=False)

  def __str__(self) -> str:
    return self.username


# chef              = models.JSONField()   # chef former value
# chef is changed from JSON field to Foreign key, so that "published" time does not change, 
# should in case the user make an update to their profile,
# of which the Recipe-Feed microservice will get the update and make the necessary changes
# chef              = models.ForeignKey(Chef, on_delete=models.DO_NOTHING) # chef new value
class Recipe(models.Model):
  title             = models.CharField(max_length=300)
  description       = models.CharField(max_length=500)
  ingredients       = ArrayField( models.JSONField() )
  instructions      = ArrayField( models.CharField(max_length=250) )
  preparation_time  = models.TimeField()
  cooking_time      = models.TimeField()
  servings          = models.IntegerField()
  images            = ArrayField( models.URLField(max_length=500, blank=True, null=True), size=4 )
  video             = models.URLField(max_length=500, default="", blank=True, null= True)
  thumbnail         = models.URLField(max_length=500, default="", blank=True, null= True)
  tags              = models.ManyToManyField(Tag)
  nutritional_value = models.JSONField(default=dict)
  chef              = models.ForeignKey(Chef, on_delete=models.DO_NOTHING, related_name='recipes', db_index=True)
  status            = models.CharField(max_length=10, choices=choices.RECIPE_STATUS_CHOICES, default="DRAFT", db_index=True)
  created           = models.DateTimeField(auto_now_add=True)
  published         = models.DateTimeField(auto_now=True)


  def __str__(self) -> str:
    return self.title
  
  # def tag_names(self):
  #   return ', '.join([tag.name for tag in self.tags.all()])
  # tag_names.short_description = "Tag Names"



class Like(models.Model):
  liker = models.ForeignKey(Chef, on_delete=models.DO_NOTHING)
  recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="likes")

  def __str__(self) -> str:
    return self.liker.username


class UpVote(models.Model):
  voter = models.ForeignKey(Chef, on_delete=models.DO_NOTHING)
  recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="upVotes")

  def __str__(self) -> str:
    return self.voter


class DownVote(models.Model):
  voter = models.ForeignKey(Chef, on_delete=models.DO_NOTHING)
  recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="downVotes")

  def __str__(self) -> str:
    return self.voter


class Comment(models.Model):
  writer  = models.ForeignKey(Chef, on_delete=models.CASCADE, related_name='comments')
  recipe  = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
  content = models.CharField(max_length=300)
  created = models.DateTimeField(auto_now_add=True)
  parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

  def __str__(self) -> str:
    return self.writer.username


class SavedRecipe(models.Model):
  chef   = models.ForeignKey(Chef, on_delete=models.CASCADE, related_name='saves', db_index=True)
  recipe  = models.ForeignKey(Recipe, on_delete=models.CASCADE, db_index=True)

  def __str__(self) -> str:
    return self.chef.username

