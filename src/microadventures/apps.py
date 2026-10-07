from django.apps import AppConfig


class MicroAdventureConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "microadventures"
    verbose_name = "MicroAdventure"
