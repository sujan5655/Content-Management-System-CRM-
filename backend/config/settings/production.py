from .base import *

DEBUG = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="",
    cast=lambda value: [
        host.strip()
        for host in value.split(",")
        if host.strip()
    ]
)