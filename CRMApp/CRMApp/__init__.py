from __future__ import absolute_import, unicode_literals
# Import the celery application to ensure it is loaded with Django
from .celery import app as celery_app

__all__ = ('celery_app',)
