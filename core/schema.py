from ariadne import QueryType, load_schema_from_path, make_executable_schema, MutationType

type_defs = load_schema_from_path('schemas')

query = QueryType()


mutation = MutationType()

schema = make_executable_schema(type_defs, query, mutation, convert_names_case=True)