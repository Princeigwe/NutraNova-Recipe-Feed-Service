from threading import Thread
from recipes.models import Recipe, Chef, Like


class LikeRecipeThread(Thread):
  def __init__(self, liker, recipe):
    Thread.__init__(self)
    self.liker = liker
    self.recipe = recipe

  def run(self):
    try:
      recipe = Recipe.objects.get(id=self.recipe.id, status='PUBLISHED')
      chef, created = Chef.objects.get_or_create(username=self.liker['username'], first_name=self.liker['first_name'], last_name=self.liker['last_name'])
      Like.objects.get(recipe=recipe.id, liker=chef.id)
    except Like.DoesNotExist:
      like = Like.objects.create(recipe=recipe, liker=chef)
      like.save()
    except Recipe.DoesNotExist as error:
      print( Exception(error) )