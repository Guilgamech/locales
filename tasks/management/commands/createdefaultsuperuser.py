import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

log = logging.getLogger("tasks")


class Command(BaseCommand):
    help = 'Crea el usuario administrador predeterminado'

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin_exists = user_model.objects.filter(username="admin").exists()
        verbose_mode_is_enabled = options['verbosity'] >= 2

        if admin_exists:
            if verbose_mode_is_enabled:
                self.stdout.write(self.style.NOTICE(
                    'El usuario administrador predeterminado ya existe'
                ))
        else:
            user_model.objects.create_superuser(
                "admin", "admin@example.com", "secret"
            )
            if verbose_mode_is_enabled:
                self.stdout.write(self.style.SUCCESS(
                    'El usuario administrador predeterminado ha sido creado'
                ))
