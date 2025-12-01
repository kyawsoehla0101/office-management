import os

ENV = os.environ.get("DJANGO_ENV", "production")

if ENV == "development":
    from .development import *
else:
    from .production import *
