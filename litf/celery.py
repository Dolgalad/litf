import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "litf.settings")

app=Celery("litf")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

#@app.on_after_configure.connect
#def setup_periodic_tasks(sender, **kwargs):
#    sender.add_periodic_task(10.0, debug_task.s(), name="imqoin")
