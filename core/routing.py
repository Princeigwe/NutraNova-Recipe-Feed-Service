from ariadne.asgi import GraphQL
from .schema import schema
from django.urls import path, re_path
from ariadne.asgi.handlers import GraphQLTransportWSHandler
from django.core.asgi import get_asgi_application



websocket_urlpatterns = [
  path("graphql/", GraphQL(schema=schema, websocket_handler=GraphQLTransportWSHandler(), debug=True)),
  re_path(r"", get_asgi_application()),
]