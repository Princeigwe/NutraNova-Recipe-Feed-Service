"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from ariadne.asgi import GraphQL
from channels.routing import URLRouter
from .schema import schema
from django.urls import path, re_path
from ariadne.asgi.handlers import GraphQLTransportWSHandler
from channels.sessions import SessionMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# application = get_asgi_application()

# wrapping SessionMiddlewareStack enabled request session in ASGI server
application = SessionMiddlewareStack( 
    URLRouter([
      path("graphql/", GraphQL(schema=schema, websocket_handler=GraphQLTransportWSHandler(), debug=True)),
      re_path(r"", get_asgi_application())
    ])
  )


# application = URLRouter([
#       path("graphql/", GraphQL(schema=schema, websocket_handler=GraphQLTransportWSHandler(), debug=True)),
#       re_path(r"", get_asgi_application())
#     ])

# app = application