from django import forms
from django.forms import TextInput, CheckboxInput, ModelChoiceField, CharField, DateInput, TimeInput, HiddenInput

from .models import Solicitud, Trabajador, Aseguramiento, Local, TipoActividad, Area, AseguramientoSolicitud, TipoAseguramiento, Actividad, TipoUsuario

class TrabajadorForm(forms.ModelForm):
    area = ModelChoiceField(Area.objects.all(), empty_label='Seleccione', label='Area:')
    tipoUsuario = ModelChoiceField(TipoUsuario.objects.all(), empty_label='Seleccione', label='Tipo de usuario:')

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['nombre'].required = True
        self.fields['apellidos'].required = True

    class Meta:
        model = Trabajador
        fields = ['nombre', 'apellidos', 'telefono', 'telefonoFijo', 'area', 'tipoUsuario']
        widgets = {
            'telefono': TextInput(attrs={'placeholder': '52037685', 'class': 'form-control'}),
            'telefonoFijo': TextInput(attrs={'placeholder': '32690107', 'class': 'form-control'})
        }
        labels = {
            'nombre':'Nombre:',
            'apellidos':'Apellidos:',
            'telefono': 'Teléfono:',
            'telefonoFijo': 'Teléfono fijo:'
        }


class SolicitudForm(forms.ModelForm):
    local = ModelChoiceField(Local.objects.all(), empty_label='Seleccione')
    tipoActividad = ModelChoiceField(TipoActividad.objects.all(), empty_label='Seleccione', label='Tipo de actividad:')
    tipoAseguramiento = ModelChoiceField(TipoAseguramiento.objects.all(), empty_label='Seleccione',
                                         label='Tipo de aseguramiento:')
    aseguramiento = ModelChoiceField(Aseguramiento.objects.all(), empty_label='Seleccione')
    descripcionAseguramiento = CharField(label='Descripción', widget=forms.Textarea())
    observacionAseguramiento = CharField(label='Observación', widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['aseguramiento'].required = False  # solo con los campos que especificaste en la clase Meta
        self.fields['descripcion'].required = False
        self.fields['observacion'].required = False
        self.fields['descripcionAseguramiento'].required = False
        self.fields['observacionAseguramiento'].required = False
        self.fields['tipoAseguramiento'].required = False

    class Meta:
        model = Solicitud
        fields = ['nombre', 'descripcion', 'observacion', 'fechaInicio', 'fechaFin', 'horaInicio', 'horaFin',
                  'diaCompleto', 'cantidadParticipante', 'local', 'tipoActividad', 'tipoAseguramiento','aseguramiento',
                  'descripcionAseguramiento', 'observacionAseguramiento', 'solicitante']
        widgets = {
            'solicitante': HiddenInput(),
            'cantidadParticipante': TextInput(attrs={'class': 'spinner-input form-control'}),
            'diaCompleto': CheckboxInput(attrs={'data-plugin-ios-switch': ''}),
            'fechaInicio': DateInput(format='%Y-%m-%d'),
            'fechaFin': DateInput(format='%Y-%m-%d'),
            'horaInicio': TimeInput(format='%H:%M'),
            'horaFin': TimeInput(format='%H:%M')
        }
        labels = {
            'solicitante': 'Trabajador:',
            'descripcion': 'Descripción:',
            'observacion': 'Observación:',
            'cantidadParticipante': 'Cantidad de participantes:',
            'tipoActividad': 'Tipo de actividad:',
            'fechaInicio': 'Fecha de inicio:',
            'fechaFin': 'Fecha final:',
            'horaInicio': 'Hora de inicio:',
            'horaFin': 'Hora final:',
            'diaCompleto': 'Todo el día:',
            'descripcionAseguramiento': 'Descripción:',
            'observacionAseguramiento': 'Observación:',
        }


class SolicitudEditForm(forms.ModelForm):
    local = ModelChoiceField(Local.objects.all(), empty_label='Seleccione')
    tipoActividad = ModelChoiceField(TipoActividad.objects.all(), empty_label='Seleccione',
                                     label='Tipo de actividad:')

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['descripcion'].required = False  # solo con los campos que especificaste en la clase Meta
        self.fields['observacion'].required = False

    class Meta:
        model = Solicitud
        fields = ['nombre', 'descripcion', 'observacion', 'fechaInicio', 'fechaFin', 'horaInicio', 'horaFin',
                  'diaCompleto', 'cantidadParticipante', 'local', 'tipoActividad']
        widgets = {
            'cantidadParticipante': TextInput(attrs={'class': 'spinner-input form-control'}),
            'diaCompleto': CheckboxInput(attrs={'data-plugin-ios-switch': ''}),
            'fechaInicio': DateInput(format='%Y-%m-%d'),
            'fechaFin': DateInput(format='%Y-%m-%d'),
            'horaInicio': TimeInput(format='%H:%M'),
            'horaFin': TimeInput(format='%H:%M')
        }
        labels = {
            'descripcion': 'Descripción:',
            'observacion': 'Observación:',
            'cantidadParticipante': 'Cantidad de participantes:',
            'tipoActividad': 'Tipo de actividad:',
            'fechaInicio': 'Fecha de inicio:',
            'fechaFin': 'Fecha final:',
            'horaInicio': 'Hora de inicio:',
            'horaFin': 'Hora final:',
            'diaCompleto': 'Todo el día:'
        }
        # help_texts = {
        #     'descripcion': 'Some useful help text.',
        # }
        # error_messages = {
        #     'descripcion': {
        #         'max_length': "This writer's name is too long.",
        #     },
        # }


# ASEGURAMIENTO_CHOICES=[]
# aseguramientos = Aseguramiento.objects.all()
# for a in aseguramientos:
#     ASEGURAMIENTO_CHOICES.append([a.pk,a.nombre])
# class AseguramientoForm(forms.Form):
#     aseguramiento=forms.MultipleChoiceField(choices = ASEGURAMIENTO_CHOICES)

class AseguramientoSolicitudForm(forms.ModelForm):
    tipoAseguramiento = ModelChoiceField(TipoAseguramiento.objects.all(), empty_label='Seleccione',
                                         label='Tipo de aseguramiento:')
    aseguramiento = ModelChoiceField(Aseguramiento.objects.all(), empty_label='Seleccione')

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['descripcion'].required = False  # solo con los campos que especificaste en la clase Meta
        self.fields['observacion'].required = False

    class Meta:
        model = AseguramientoSolicitud
        fields = ['tipoAseguramiento', 'aseguramiento', 'descripcion', 'observacion']
        labels = {
            'tipoAseguramiento': 'Tipo de aseguramiento:',
            'aseguramiento': 'Aseguramiento:',
            'descripcion': 'Descripción:',
            'observacion': 'Observación:',
        }

class ActividadForm(forms.ModelForm):

    tipoActividad = ModelChoiceField(TipoActividad.objects.all(), empty_label='Seleccione', label='Tipo de actividad:')

    def __init__(self, locales,*args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['local'] = ModelChoiceField(locales, empty_label='Seleccione')
        self.fields['descripcion'].required = False

    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'fechaInicio', 'fechaFin', 'horaInicio', 'horaFin',
                  'local', 'tipoActividad']
        widgets = {
            'fechaInicio': DateInput(format='%Y-%m-%d'),
            'fechaFin': DateInput(format='%Y-%m-%d'),
            'horaInicio': TimeInput(format='%H:%M'),
            'horaFin': TimeInput(format='%H:%M')
        }
        labels = {
            'descripcion': 'Descripción:',
            'tipoActividad': 'Tipo de actividad:',
            'fechaInicio': 'Fecha de inicio:',
            'fechaFin': 'Fecha final:',
            'horaInicio': 'Hora de inicio:',
            'horaFin': 'Hora final:',
        }