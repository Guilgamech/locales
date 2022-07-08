from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import re
from django.core.exceptions import ValidationError
from django.db.models import Q

from setuptools._distutils.command.bdist import bdist


class ValidateOnSaveMixin(object):
    def save(self, *args, **kwargs):
        self.full_clean()
        super(ValidateOnSaveMixin, self).save(*args, **kwargs)


class TipoActividad(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre


class Area(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre


class TipoAseguramiento(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre


class TipoUsuario(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre


class Aseguramiento(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    tipoAseguramiento = models.ForeignKey(TipoAseguramiento, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Trabajador(models.Model):
    nombre = models.CharField(max_length=255, blank=True, default='')
    apellidos = models.CharField(max_length=255, blank=True, default='')
    user = models.OneToOneField(User, related_name='user', verbose_name='Usuario', on_delete=models.CASCADE, null=True,
                                blank=True)
    expreRegular = re.compile(r'^[0-9\s+()-]+\Z')
    validatePhone = RegexValidator(expreRegular, "Introduzca un 'NÚMERO DE TELÉFONO' válido.", 'error')
    telefono = models.CharField('teléfono personal', max_length=20, blank=True, null=True, validators=[validatePhone],
                                default='')
    telefonoFijo = models.CharField('teléfono fijo', max_length=20, blank=True, null=True, validators=[validatePhone],
                                    default='')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(blank=False, null=False, unique=True, default='')
    tipoUsuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE, null=False, blank=False, default='')

    def __str__(self):
        return self.nombre + ' ' + self.apellidos

    class Meta:
        verbose_name = 'trabajador'
        verbose_name_plural = 'trabajadores'


class Local(models.Model):
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    capacidad = models.IntegerField()
    telefono = models.IntegerField(null=True, blank=True)
    responsables = models.ManyToManyField(Trabajador, blank=True, related_name='responsables')

    def __str__(self):
        return self.nombre


class Solicitud(ValidateOnSaveMixin, models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(max_length=255, null=True, blank=True)
    observacion = models.TextField(max_length=255, null=True, blank=True)
    fechaInicio = models.DateField('fecha de inicio')
    fechaFin = models.DateField('fecha de fin')
    horaInicio = models.TimeField('hora de inicio', null=True, blank=True)
    horaFin = models.TimeField('hora de fin', null=True, blank=True)
    diaCompleto = models.BooleanField('todo el día', default=False)
    cantidadParticipante = models.IntegerField(null=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, default=1)
    solicitante = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    tipoActividad = models.ForeignKey(TipoActividad, on_delete=models.CASCADE)

    def clean(self):
        try:
            # Validar que la fecha de inicio sea anterior a la fecha de fin
            if self.fechaInicio > self.fechaFin:
                raise ValidationError({
                    'fechaInicio': ValidationError('La fecha de inicio debe ser anterior a la fecha de fin',
                                                   code='too_late_date'),
                    'fechaFin': ValidationError('La fecha de fin debe ser posterior a la fecha de inicio',
                                                code='too_early_date'),
                })

            actividad = Actividad.objects.filter(local=self.local).filter(
                Q(fechaInicio__gte=self.fechaInicio, fechaFin__gte=self.fechaFin) &
                (Q(horaInicio__gte=self.horaInicio, horaFin__gt=self.horaInicio) |
                Q(horaInicio__lte=self.horaInicio, horaFin__gt=self.horaInicio))
            ).exclude(id=self.pk)

            if actividad.count() != 0:
                message = "El lugar con el rango de fecha y hora coincide con alguna otra actividad planificada"
                raise ValidationError({
                    '__all__': message,
                    'local': "El lugar: " + self.local.__str__() + " está ocupado en ese momento.",
                    'fechaInicio': "Fecha ocupada",
                    'fechaFin': "Fecha ocupada",
                    'horaInicio': "Hora ocupada",
                    'horaFin': "Hora ocupada",
                })
            hayDatos = Solicitud.objects.all()
            if hayDatos.count() != 0:
                # Buscar solicitudes en el mismo lugar y rango de fecha de un solicitante
                solicitud = Solicitud.objects.filter(solicitante=self.solicitante).filter(local=self.local).filter(
                    Q(fechaInicio__gte=self.fechaInicio, fechaFin__gte=self.fechaFin) &
                    (Q(horaInicio__gte=self.horaInicio, horaFin__gt=self.horaInicio) |
                    Q(horaInicio__lte=self.horaInicio, horaFin__gt=self.horaInicio))
                ).exclude(id=self.pk)
                # Validar que no haya solicitudes en el mismo lugar y rango de fecha
                if solicitud.count() != 0:
                    message = "El lugar con el rango de fecha y hora coincide con alguna otra solicitud"
                    raise ValidationError({
                        '__all__': message,
                        'local': "El lugar: " + self.local.__str__() + " está ocupado en ese momento.",
                        'fechaInicio': "Fecha ocupada",
                        'fechaFin': "Fecha ocupada",
                        'horaInicio': "Hora ocupada",
                        'horaFin': "Hora ocupada",
                    })
        except (Local.DoesNotExist):
            pass

    def __str__(self):
        return self.nombre


class AseguramientoLocal(models.Model):
    aseguramiento = models.ForeignKey(Aseguramiento, on_delete=models.CASCADE)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    cantidad = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.local.__str__() + ' - ' + self.aseguramiento.__str__()


class AseguramientoSolicitud(models.Model):
    aseguramiento = models.ForeignKey(Aseguramiento, on_delete=models.CASCADE)
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    descripcion = models.TextField(max_length=255, null=True)
    observacion = models.TextField(max_length=255, null=True)


class Actividad(ValidateOnSaveMixin, models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(max_length=255, null=True, blank=True)
    fechaInicio = models.DateField('fecha de inicio', null=False, blank=False)
    fechaFin = models.DateField('fecha de fin', null=False, blank=False)
    horaInicio = models.TimeField('hora de inicio', null=False, blank=False)
    horaFin = models.TimeField('hora de fin', null=False, blank=False)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    tipoActividad = models.ForeignKey(TipoActividad, on_delete=models.CASCADE)

    def clean(self):
        try:
            # Validar que la fecha de inicio sea anterior a la fecha de fin
            if self.fechaInicio > self.fechaFin:
                raise ValidationError({
                    'fechaInicio': ValidationError('La fecha de inicio debe ser anterior a la fecha de fin',
                                                   code='too_late_date'),
                    'fechaFin': ValidationError('La fecha de fin debe ser posterior a la fecha de inicio',
                                                code='too_early_date'),
                })

            # Buscar actividades en el mismo lugar y rango de fecha
            actividad = Actividad.objects.filter( local=self.local).filter(
                Q(fechaInicio__gte=self.fechaInicio, fechaFin__gte=self.fechaFin) &
                (Q(horaInicio__gte=self.horaInicio, horaFin__gt=self.horaInicio) |
                Q(horaInicio__lte=self.horaInicio, horaFin__gt=self.horaInicio))
            ).exclude(id=self.pk)

            # Validar que no haya actividades en el mismo lugar y rango de fecha
            if actividad.count() > 0:
                message = "El lugar y rango de fecha coincide con los de otra actividad"
                if self.local:
                    raise ValidationError({
                        '__all__': message,
                        'local': "El lugar: " + self.local.__str__() + " está ocupado",
                        'fechaInicio': "Fecha ocupada",
                        'fechaFin': "Fecha ocupada",
                        'horaInicio': "Hora ocupada",
                        'horaFin': "Hora ocupada",
                    })
        except (Local.DoesNotExist):
            pass

    def __str__(self):
        return self.nombre
