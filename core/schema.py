from ariadne import QueryType, load_schema_from_path, make_executable_schema, MutationType
from recipes import resolvers

type_defs = load_schema_from_path('schemas')

query = QueryType()
query.set_field("recipeTags", resolvers.resolve_recipe_tags)


mutation = MutationType()
mutation.set_field("createRecipe", resolvers.resolve_create_recipe)
mutation.set_field("editRecipe", resolvers.resolve_edit_recipe)

schema = make_executable_schema(type_defs, query, mutation, convert_names_case=True)