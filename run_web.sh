#!/bin/sh

# Aplicar las migraciones de BD
python manage.py migrate

# Crear superuser predeterminado
python manage.py createdefaultsuperuser
