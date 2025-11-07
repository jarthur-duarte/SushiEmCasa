from django.apps import AppConfig
from django.db.models.signals import post_migrate


class SushiemcasaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sushiemcasa'

from django.apps import AppConfig
class SushiemcasaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sushiemcasa'

    def ready(self):
        import sushiemcasa.signals