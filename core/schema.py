from ariadne import QueryType, load_schema_from_path, make_executable_schema, MutationType, SubscriptionType
from recipes import resolvers

type_defs = load_schema_from_path('schemas')

query = QueryType()
query.set_field("recipeTags", resolvers.resolve_recipe_tags)
query.set_field("recipeFeed", resolvers.resolve_recipe_feed)
# query.set_field("singleRecipe", resolvers.resolve_single_recipe)
query.set_field("myDrafts", resolvers.resolve_my_drafts)
query.set_field("draft", resolvers.resolve_draft)
query.set_field("myPublishedRecipes", resolvers.resolve_my_published_recipes)
query.set_field("search", resolvers.resolve_search)
query.set_field("recipeComments", resolvers.resolve_recipe_comments)
query.set_field("mySavedRecipes", resolvers.resolve_my_saved_recipes)
query.set_field("commentReplies", resolvers.resolve_comment_replies)

mutation = MutationType()
mutation.set_field("createRecipe", resolvers.resolve_create_recipe)
mutation.set_field("editRecipe", resolvers.resolve_edit_recipe)
mutation.set_field("likeRecipe", resolvers.resolve_like_recipe)
mutation.set_field("unLikeRecipe", resolvers.resolve_unlike_recipe)
mutation.set_field("deleteRecipe", resolvers.resolve_delete_recipe)
mutation.set_field("commentOnRecipe", resolvers.resolve_comment_on_recipe)
mutation.set_field("saveForLater", resolvers.resolve_save_for_later)
mutation.set_field("commentOnComment", resolvers.resolve_comment_on_comment)
mutation.set_field("upVoteRecipe", resolvers.resolve_up_vote_recipe)

subscription = SubscriptionType()
subscription.set_field("singleRecipe", resolvers.resolve_single_recipe_sub)
subscription.set_source("singleRecipe", resolvers.single_recipe_sub_generator)

schema = make_executable_schema(type_defs, query, mutation, subscription, convert_names_case=True)