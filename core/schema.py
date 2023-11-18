from ariadne import QueryType, load_schema_from_path, make_executable_schema, MutationType
from recipes import resolvers

type_defs = load_schema_from_path('schemas')

query = QueryType()


mutation = MutationType()
mutation.set_field("createRecipe", resolvers.resolve_create_recipe)

schema = make_executable_schema(type_defs, query, mutation, convert_names_case=True)