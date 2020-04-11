from __future__ import absolute_import, unicode_literals

from celery import shared_task
from .models import Borough

@shared_task
def update_borough_database():
        pass
