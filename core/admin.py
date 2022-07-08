from django.contrib import admin
from . import models

admin.site.register(models.Area)
admin.site.register(models.TipoActividad)
admin.site.register(models.Estado)
admin.site.register(models.Local)
admin.site.register(models.AseguramientoLocal)
admin.site.register(models.TipoAseguramiento)
admin.site.register(models.Aseguramiento)
admin.site.register(models.Trabajador)
admin.site.register(models.TipoUsuario)