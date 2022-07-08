from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Aseguramiento, Local, Solicitud, Trabajador, AseguramientoSolicitud, TipoAseguramiento, Estado, \
    Actividad
from .form import SolicitudForm, SolicitudEditForm, TrabajadorForm, AseguramientoSolicitudForm, ActividadForm
import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseServerError
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages

from django.db.models import Q


@login_required(login_url='/login/')
def proxy(request):
    user = request.user
    trabajador = Trabajador.objects.get(email=user.email)
    if trabajador != None:
        trabajador.user = user
        trabajador.save()
        return redirect('/solicitud/new/')
    else:
        return redirect('/perfil/')


@login_required(login_url='/login/')
def dashboard(request):
    user = request.user
    findTrabajador = Trabajador.objects.filter(user=user)
    if findTrabajador.exists():
        trabajador = findTrabajador[0]
        locales = Local.objects.all()
        if user.groups.filter(name='responsable_local').exists():
            locales = Local.objects.filter(responsables=trabajador)
        return render(request, 'default/dashboard.html', {'user': request.user, 'locales': locales})
    else:
        return redirect('/perfil/')


def calendario(request):
    user = request.user
    trabajador = Trabajador.objects.get(user=user)
    datos = []
    color = ''
    if user.groups.filter(name='responsable_local').exists():
        locales = Local.objects.filter(responsables=trabajador)

        for local in locales:
            solicituds = Solicitud.objects.filter(local=local)
            actividads = Actividad.objects.filter(local=local)
            for solicitud in solicituds:
                if solicitud.estado.id != 3:
                    if solicitud.estado.id == 2:
                        color = 'green'
                    if solicitud.estado.id == 1:
                        color = 'red'
                    item = {
                        'id': solicitud.id,
                        'title': solicitud.nombre,
                        'descripcion': solicitud.descripcion,
                        'observacion': solicitud.observacion,
                        'start': datetime.strftime(solicitud.fechaInicio, "%Y-%m-%d") + 'T' + str(solicitud.horaInicio),
                        'end': datetime.strftime(solicitud.fechaFin, "%Y-%m-%d") + 'T' + str(solicitud.horaFin),
                        'allDay': solicitud.diaCompleto,
                        'cantidadParticipante': solicitud.cantidadParticipante,
                        'estado': solicitud.estado.__str__(),
                        'estado_id': solicitud.estado.id,
                        'solicitante': solicitud.solicitante.__str__(),
                        'tipoUsuario': solicitud.solicitante.tipoUsuario.__str__(),
                        'local': solicitud.local.__str__(),
                        'tipoActividad': solicitud.tipoActividad.__str__(),
                        'color': color,
                        'textColor': 'white',
                        'esSolicitud': True
                    }
                    datos.append(item)

            for actividad in actividads:
                color = '#f4b600'

                item = {
                    'id': actividad.id,
                    'title': actividad.nombre,
                    'descripcion': actividad.descripcion,
                    'start': datetime.strftime(actividad.fechaInicio, "%Y-%m-%d") + 'T' + str(
                        actividad.horaInicio),
                    'end': datetime.strftime(actividad.fechaFin, "%Y-%m-%d") + 'T' + str(actividad.horaFin),
                    'allDay': False,
                    'local': actividad.local.__str__(),
                    'tipoActividad': actividad.tipoActividad.__str__(),
                    'color': color,
                    'textColor': 'white',
                    'esSolicitud': False
                }
                datos.append(item)

    else:
        solicituds = Solicitud.objects.filter(solicitante=trabajador)
        actividads = Actividad.objects.all()
        for solicitud in solicituds:
            if solicitud.estado.id != 3:
                if solicitud.estado.id == 2:
                    color = 'green'
                if solicitud.estado.id == 1:
                    color = 'red'
                item = {
                    'id': solicitud.id,
                    'title': solicitud.nombre,
                    'descripcion': solicitud.descripcion,
                    'observacion': solicitud.observacion,
                    'start': datetime.strftime(solicitud.fechaInicio, "%Y-%m-%d") + 'T' + str(solicitud.horaInicio),
                    'end': datetime.strftime(solicitud.fechaFin, "%Y-%m-%d") + 'T' + str(solicitud.horaFin),
                    'allDay': solicitud.diaCompleto,
                    'cantidadParticipante': solicitud.cantidadParticipante,
                    'estado': solicitud.estado.__str__(),
                    'solicitante': solicitud.solicitante.__str__(),
                    'tipoUsuario': solicitud.solicitante.tipoUsuario.__str__(),
                    'local': solicitud.local.__str__(),
                    'tipoActividad': solicitud.tipoActividad.__str__(),
                    'color': color,
                    'textColor': 'white',
                    'esSolicitud': True
                }
                datos.append(item)

        for actividad in actividads:
            color = '#f4b600'

            item = {
                'id': actividad.id,
                'title': actividad.nombre,
                'descripcion': actividad.descripcion,
                'start': datetime.strftime(actividad.fechaInicio, "%Y-%m-%d") + 'T' + str(
                    actividad.horaInicio),
                'end': datetime.strftime(actividad.fechaFin, "%Y-%m-%d") + 'T' + str(actividad.horaFin),
                'allDay': False,
                'local': actividad.local.__str__(),
                'tipoActividad': actividad.tipoActividad.__str__(),
                'color': color,
                'textColor': 'white',
                'esSolicitud': False
            }
            datos.append(item)
    # convertir eso en un json

    datos = json.dumps(datos)

    return HttpResponse(datos, content_type='application/json')
    # return JsonResponse(datos, safe=False)


@login_required(login_url='/login/')
def trabajadorEdit(request):
    user = request.user
    findTrabajador = Trabajador.objects.filter(user=user)
    if findTrabajador.exists():
        trabajador = findTrabajador[0]
    else:
        trabajador = Trabajador()
        trabajador.nombre = user.first_name
        trabajador.apellidos = user.last_name

    if request.method == 'POST':
        form = TrabajadorForm(request.POST)
        if form.is_valid():
            trabajador = form.save(commit=False)
            area = trabajador.area
            telefono = trabajador.telefono
            telefonoFijo = trabajador.telefonoFijo
            tipoUsuario = trabajador.tipoUsuario
            findTrabajador = Trabajador.objects.filter(user=user)
            if findTrabajador.exists():
                trabajador = findTrabajador[0]

            trabajador.telefono = telefono
            trabajador.telefonoFijo = telefonoFijo
            trabajador.area = area
            trabajador.tipoUsuario = tipoUsuario
            trabajador.user = user
            trabajador.email = user.email
            trabajador.save()
            messages.success(request, 'Se a actualizado su perfil.')
            return redirect('/')
        messages.error(request, 'No se ha podido actualizar su perfil.')
    else:
        form = TrabajadorForm(instance=trabajador)

    return render(request, 'trabajador/edit.html', {'form': form})


@login_required(login_url='/login/')
def trabajadorDelete(request, trabajador_id):
    trabajador = Trabajador.objects.get(pk=trabajador_id)
    trabajador.delete()
    messages.success(request, 'Se elimino el trabajador.')
    return redirect('/')


@login_required(login_url='/login/')
def solicitudIndex(request):
    user = request.user
    existe = Trabajador.objects.filter(user=user).exists()
    if existe == False:
        return redirect('/perfil/')
    trabajador = Trabajador.objects.get(user=user)

    solicituds = []
    if user.groups.filter(name='responsable_local').exists():
        locales = Local.objects.filter(responsables=trabajador)
        for local in locales:
            solicitudLocal = Solicitud.objects.filter(local=local)
            for solicitud in solicitudLocal:
                solicituds.append(solicitud)

    else:
        solicituds = Solicitud.objects.filter(solicitante=trabajador)

    context = {'solicituds': solicituds}
    return render(request, 'solicitud/index.html', context)


@login_required(login_url='/login/')
def solicitudNew(request):
    aseguramientos = Aseguramiento.objects.all()
    tipoAseguramientos = TipoAseguramiento.objects.all()
    trabajador = Trabajador.objects.get(user_id=request.user)
    solicitud = Solicitud()
    solicitud.solicitante = trabajador
    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.save()
            elementos = request.POST.get('elementos')
            for x in range(1, int(elementos) + 1):
                solicitud = Solicitud.objects.get(pk=solicitud.pk)
                aseguramiento = Aseguramiento.objects.get(pk=request.POST.get('aseguramiento_' + str(x)))
                aseguramientoSolicitud = AseguramientoSolicitud(solicitud=solicitud, aseguramiento=aseguramiento,
                                                                descripcion=request.POST.get('descripcion_' + str(x)),
                                                                observacion=request.POST.get('observacion_' + str(x)))
                aseguramientoSolicitud.save()

            local = Local.objects.get(id=solicitud.local_id)
            responsables = local.responsables.all()

            # enviando correo al responsable del local
            if responsables.count() != 0:

                for responsable in responsables:
                    subject = 'Solicitud pendiente'
                    from_email = settings.EMAIL_FROM
                    to = responsable.user.email
                    text_content = 'Tienes una solicitud pendiente en tu local:\n https://sgrl.reduc.edu.cu/solicitud/' + str(
                        solicitud.id) + '/show/'
                    html_content = '<body>Tienes una solicitud pendiente en tu local:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
                        solicitud.id) + '/show/>Solicitud pendiente</a>.</body>'
                    msg = EmailMultiAlternatives(
                        subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

            messages.success(request, 'Solicitud creada con exito.')

            return redirect('/solicitud/index/')
        messages.error(request, 'La solicitud no se pudo crear.')
    else:
        form = SolicitudForm(instance=solicitud)

    return render(request, 'solicitud/new.html',
                  {'form': form, 'aseguramientos': aseguramientos, 'tipoAseguramientos': tipoAseguramientos})


@login_required(login_url='/login/')
def solicitudCreateAndNew(request):
    aseguramientos = Aseguramiento.objects.all()
    tipoAseguramientos = TipoAseguramiento.objects.all()

    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            trabajador = Trabajador.objects.get(user_id=request.user)
            solicitud.solicitante = trabajador
            solicitud.save()
            elementos = request.POST.get('elementos')
            for x in range(1, int(elementos) + 1):
                solicitud = Solicitud.objects.get(pk=solicitud.pk)
                aseguramiento = Aseguramiento.objects.get(pk=request.POST.get('aseguramiento_' + str(x)))
                aseguramientoSolicitud = AseguramientoSolicitud(solicitud=solicitud, aseguramiento=aseguramiento,
                                                                descripcion=request.POST.get('descripcion_' + str(x)),
                                                                observacion=request.POST.get('observacion_' + str(x)))
                aseguramientoSolicitud.save()

            local = Local.objects.get(id=solicitud.local_id)
            responsables = local.responsables.all()

            # enviando correo al responsable del local
            if responsables.count() != 0:

                for responsable in responsables:
                    subject = 'Solicitud pendiente'
                    from_email = settings.EMAIL_FROM
                    to = responsable.user.email
                    text_content = 'Tienes una solicitud pendiente en tu local:\nhttps://sgrl.reduc.edu.cu/solicitud/' + str(
                        solicitud.id) + '/show/'
                    html_content = '<body>Tienes una solicitud pendiente en tu local:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
                        solicitud.id) + '/show/>Solicitud pendiente</a>.</body>'
                    msg = EmailMultiAlternatives(
                        subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

            messages.success(request, 'Solicitud creada con exito.')

            return redirect('/solicitud/new/')
        messages.error(request, 'La solicitud no se pudo crear.')
    else:
        form = SolicitudForm()

    return render(request, 'solicitud/new.html',
                  {'form': form, 'aseguramientos': aseguramientos, 'tipoAseguramientos': tipoAseguramientos})


@login_required(login_url='/login/')
def solicitudShow(request, solicitud_id):
    user = request.user
    solicitud = Solicitud.objects.get(pk=solicitud_id)
    aseguramientos = AseguramientoSolicitud.objects.filter(solicitud=solicitud)
    responsable = False
    if user.groups.filter(name='responsable_local').exists():
        responsable = True
    context = {'solicitud': solicitud, 'aseguramientos': aseguramientos, 'responsable': responsable}
    return render(request, 'solicitud/show.html', context)


@login_required(login_url='/login/')
def solicitudEdit(request, solicitud_id):
    solicitud = Solicitud.objects.get(pk=solicitud_id)
    aseguramientos = AseguramientoSolicitud.objects.filter(solicitud=solicitud)
    if request.method == 'POST':
        form = SolicitudEditForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, 'Se a editado dicha solicitud.')
            return redirect('/solicitud/index/')
        messages.error(request, 'No se ha podido editar la solicitud.')
    else:
        form = SolicitudEditForm(instance=solicitud)

    return render(request, 'solicitud/edit.html',
                  {'form': form, 'solicitud': solicitud, 'aseguramientos': aseguramientos})


@login_required(login_url='/login/')
def solicitudDelete(request, solicitud_id):
    solicitud = Solicitud.objects.get(pk=solicitud_id)
    solicitud.delete()
    messages.success(request, 'La solicitud se elimino correctamente.')
    return redirect('/solicitud/index/')


@login_required(login_url='/login/')
def solicitudDeleteAll(request):
    datos = request.POST.getlist('select[]')
    for dato in datos:
        solicitud = Solicitud.objects.get(pk=dato)
        solicitud.delete()
    if len(datos) == 1:
        messages.success(request, 'La solicitud se elimino correctamente.')
    else:
        messages.success(request, 'Las solicitudes se eliminaron correctamente.')
    return redirect('/solicitud/index/')


@login_required(login_url='/login/')
def solicitudAceptarAll(request):
    datos = request.POST.getlist('select[]')
    estado = Estado.objects.get(pk=2)
    encontradas = 0
    for dato in datos:
        findSolicitud = Solicitud.objects.get(pk=dato)
        solicitud = Solicitud.objects.filter(local=findSolicitud.local).filter(estado=estado).filter(
            Q(fechaInicio__gte=findSolicitud.fechaInicio, fechaFin__gte=findSolicitud.fechaFin) &
            (Q(horaInicio__gte=findSolicitud.horaInicio, horaFin__gt=findSolicitud.horaInicio) |
             Q(horaInicio__lte=findSolicitud.horaInicio, horaFin__gt=findSolicitud.horaInicio))
        ).exclude(id=findSolicitud.pk)
        if solicitud.count() == 0:
            solicitud = Solicitud.objects.get(pk=dato)

            solicitud.estado = estado
            solicitud.save()
            # enviando correo al trabajador que pidio la reserva del local

            subject = 'Tu solicitud ha cambiado de estado'
            from_email = settings.EMAIL_FROM
            to = solicitud.solicitante.user.email
            text_content = 'Tienes una solicitud que ha cambiado de estado:\nhttps://sgrl.reduc.edu.cu/solicitud/' + str(
                solicitud.id) + '/show/'
            html_content = '<body>Tienes una solicitud que ha cambiado de estado:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
                solicitud.id) + '/show/> Solicitud cambiada de estado. </a>.</body>'
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            encontradas = encontradas + 1
            messages.error(request, 'No se ha podido aceptar la solicitud. ' + findSolicitud.__str__())
    if encontradas == 0:
        if len(datos) == 1:
            messages.success(request, 'La solicitud se acepto correctamente.')
        else:
            messages.success(request, 'Las solicitudes se aceptaron correctamente.')
    else:
        if len(datos) == 1:
            messages.error(request, 'La solicitud no se ha podido aceptar correctamente.')
        else:
            messages.error(request, 'No se aceptraron todas las solicitudes, faltaron ' + encontradas)
    return redirect('/solicitud/index/')


@login_required(login_url='/login/')
def solicitudDenegarAll(request):
    datos = request.POST.getlist('select[]')
    estado = Estado.objects.get(pk=3)
    for dato in datos:
        solicitud = Solicitud.objects.get(pk=dato)
        solicitud.estado = estado
        solicitud.save()
        # enviando correo al trabajador que pidio la reserva del local

        subject = 'Tu solicitud ha cambiado de estado'
        from_email = settings.EMAIL_FROM
        to = solicitud.solicitante.user.email
        text_content = 'Tienes una solicitud que ha cambiado de estado:\nhttps://sgrl.reduc.edu.cu/solicitud/' + str(
            solicitud.id) + '/show/'
        html_content = '<body>Tienes una solicitud que ha cambiado de estado:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
            solicitud.id) + '/show/> Solicitud cambiada de estado. </a>.</body>'
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    if len(datos) == 1:
        messages.success(request, 'La solicitud se denego correctamente.')
    else:
        messages.success(request, 'Las solicitudes se denegaron correctamente.')
    return redirect('/solicitud/index/')

@login_required(login_url='/login/')
def solicitudAceptar(request, solicitud_id):
    findSolicitud = Solicitud.objects.get(pk=solicitud_id)
    estado = Estado.objects.get(pk=2)

    solicitud = Solicitud.objects.filter(local=findSolicitud.local).filter(estado=estado).filter(
        Q(fechaInicio__gte=findSolicitud.fechaInicio, fechaFin__gte=findSolicitud.fechaFin) &
        (Q(horaInicio__gte=findSolicitud.horaInicio, horaFin__gt=findSolicitud.horaInicio) |
         Q(horaInicio__lte=findSolicitud.horaInicio, horaFin__gt=findSolicitud.horaInicio))
    ).exclude(id=findSolicitud.pk)
    if solicitud.count() == 0:
        solicitud = findSolicitud

        solicitud.estado = estado
        solicitud.save()
        # enviando correo al trabajador que pidio la reserva del local

        subject = 'Tu solicitud ha cambiado de estado'
        from_email = settings.EMAIL_FROM
        to = solicitud.solicitante.user.email
        text_content = 'Tienes una solicitud que ha cambiado de estado:\nhttps://sgrl.reduc.edu.cu/solicitud/' + str(
            solicitud.id) + '/show/'
        html_content = '<body>Tienes una solicitud que ha cambiado de estado:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
            solicitud.id) + '/show/> Solicitud cambiada de estado. </a>.</body>'
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        messages.success(request, 'La solicitud se acepto correctamente.')
    else:
        messages.error(request, 'No se ha podido aceptar la solicitud. ' + findSolicitud.__str__())
    return redirect('/solicitud/index/')

@login_required(login_url='/login/')
def solicitudDenegar(request, solicitud_id):
    solicitud = Solicitud.objects.get(pk=solicitud_id)
    estado = Estado.objects.get(pk=3)
    solicitud.estado = estado
    solicitud.save()
    # enviando correo al trabajador que pidio la reserva del local

    subject = 'Tu solicitud ha cambiado de estado'
    from_email = settings.EMAIL_FROM
    to = solicitud.solicitante.user.email
    text_content = 'Tienes una solicitud que ha cambiado de estado:\nhttps://sgrl.reduc.edu.cu/solicitud/' + str(
        solicitud.id) + '/show/'
    html_content = '<body>Tienes una solicitud que ha cambiado de estado:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
        solicitud.id) + '/show/> Solicitud cambiada de estado. </a>.</body>'
    msg = EmailMultiAlternatives(
        subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    messages.success(request, 'La solicitud se denego correctamente.')
    return redirect('/solicitud/index/')

@login_required(login_url='/login/')
def solicitudNueva(request, local_id):
    aseguramientos = Aseguramiento.objects.all()
    tipoAseguramientos = TipoAseguramiento.objects.all()

    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            trabajador = Trabajador.objects.get(user_id=request.user)
            solicitud.solicitante = trabajador
            solicitud.save()
            elementos = request.POST.get('elementos')
            for x in range(1, int(elementos) + 1):
                solicitud = Solicitud.objects.get(pk=solicitud.pk)
                aseguramiento = Aseguramiento.objects.get(pk=request.POST.get('aseguramiento_' + str(x)))
                aseguramientoSolicitud = AseguramientoSolicitud(solicitud=solicitud, aseguramiento=aseguramiento,
                                                                descripcion=request.POST.get('descripcion_' + str(x)),
                                                                observacion=request.POST.get('observacion_' + str(x)))
                aseguramientoSolicitud.save()

            local = Local.objects.get(id=solicitud.local_id)
            responsables = local.responsables.all()

            # enviando correo al responsable del local
            if responsables.count() != 0:

                for responsable in responsables:
                    subject = 'Solicitud pendiente'
                    from_email = settings.EMAIL_FROM
                    to = responsable.user.email
                    text_content = 'Tienes una solicitud pendiente en tu local:\nhttps://sgrl.reduc.edu.cu/solicitud/' + str(
                        solicitud.id) + '/show/'
                    html_content = '<body>Tienes una solicitud pendiente en tu local:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
                        solicitud.id) + '/show/>Solicitud pendiente</a>.</body>'
                    msg = EmailMultiAlternatives(
                        subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

            messages.success(request, 'Solicitud creada con exito.')
            return redirect('/solicitud/index/')
        messages.error(request, 'La solicitud no se pudo crear.')
    else:
        form = SolicitudForm()

    return render(request, 'solicitud/nueva.html',
                  {'form': form, 'aseguramientos': aseguramientos, 'tipoAseguramientos': tipoAseguramientos,
                   'local_id': local_id})


@login_required(login_url='/login/')
def aseguramientoSolicitudNew(request, solicitud_id):
    solicitud = Solicitud.objects.get(pk=solicitud_id)

    if request.method == 'POST':
        form = AseguramientoSolicitudForm(request.POST)
        if form.is_valid():
            aseguramientoSolicitud = form.save(commit=False)
            obj = AseguramientoSolicitud.objects.filter(solicitud=solicitud,
                                                        aseguramiento=aseguramientoSolicitud.aseguramiento)

            if obj.exists():
                asegSolis = AseguramientoSolicitud.objects.get(pk=obj[0].pk)
                asegSolis.cantidad = aseguramientoSolicitud.cantidad
                asegSolis.save()
            else:
                aseguramientoSolicitud.solicitud = solicitud
                aseguramientoSolicitud.save()

            messages.success(request, 'Se a agregó el aseguramiento a dicha solicitud.')
            return redirect('solicitud_edit', solicitud_id=solicitud.id)
        messages.error(request, 'No se ha podido agregar el aseguramiento.')
    else:
        form = AseguramientoSolicitudForm()

    return render(request, 'aseguramiento_solicitud/new.html', {'form': form, 'solicitud': solicitud})


@login_required(login_url='/login/')
def aseguramientoSolicitudCreateAndNew(request, solicitud_id):
    solicitud = Solicitud.objects.get(pk=solicitud_id)

    if request.method == 'POST':
        form = AseguramientoSolicitudForm(request.POST)
        if form.is_valid():
            aseguramientoSolicitud = form.save(commit=False)
            obj = AseguramientoSolicitud.objects.filter(solicitud=solicitud,
                                                        aseguramiento=aseguramientoSolicitud.aseguramiento)

            if obj.exists():
                asegSolis = AseguramientoSolicitud.objects.get(pk=obj[0].pk)
                asegSolis.cantidad = aseguramientoSolicitud.cantidad
                asegSolis.save()
            else:
                aseguramientoSolicitud.solicitud = solicitud
                aseguramientoSolicitud.save()
            messages.success(request, 'Se a agregó el aseguramiento a dicha solicitud.')
            return redirect('aseguramiento_solicitud_new', solicitud_id=solicitud.id)
        messages.error(request, 'No se ha podido agregar el aseguramiento.')
    else:
        form = AseguramientoSolicitudForm()

    return render(request, 'aseguramiento_solicitud/new.html', {'form': form, 'solicitud': solicitud})


@login_required(login_url='/login/')
def aseguramientoSolicitudEdit(request, aseguramientoSolicitud_id):
    aseguramientoSolicitud = AseguramientoSolicitud.objects.get(pk=aseguramientoSolicitud_id)
    tipoAseguramiento = aseguramientoSolicitud.aseguramiento.tipoAseguramiento.id
    if request.method == 'POST':
        form = AseguramientoSolicitudForm(request.POST, instance=aseguramientoSolicitud)
        if form.is_valid():
            aseguramientoSolicitud = form.save(commit=False)
            obj = AseguramientoSolicitud.objects.filter(solicitud=aseguramientoSolicitud.solicitud,
                                                        aseguramiento=aseguramientoSolicitud.aseguramiento)

            if obj.exists():
                asegSolis = AseguramientoSolicitud.objects.get(pk=obj[0].pk)
                asegSolis.descripcion = aseguramientoSolicitud.descripcion
                asegSolis.observacion = aseguramientoSolicitud.observacion
                aseguramientoSolicitud.delete()
                asegSolis.save()
            else:
                aseguramientoSolicitud.save()
            messages.success(request, 'Se a editado el aseguramiento a dicha solicitud.')
            return redirect('solicitud_edit', solicitud_id=aseguramientoSolicitud.solicitud.id)
        messages.error(request, 'No se ha podido editar el aseguramiento.')
    else:
        form = AseguramientoSolicitudForm(instance=aseguramientoSolicitud)

    return render(request, 'aseguramiento_solicitud/edit.html',
                  {'form': form, 'solicitud': aseguramientoSolicitud.solicitud, 'tipoAseguramiento': tipoAseguramiento,
                   'aseguramientoSolicitud': aseguramientoSolicitud})


@login_required(login_url='/login/')
def aseguramientoSolicitudDelete(request, aseguramientoSolicitud_id):
    aseguramientoSolicitud = AseguramientoSolicitud.objects.get(pk=aseguramientoSolicitud_id)
    aseguramientoSolicitud.delete()
    messages.success(request, 'Se a eliminado el aseguramiento a dicha solicitud.')
    return redirect('solicitud_edit', solicitud_id=aseguramientoSolicitud.solicitud.id)


@login_required(login_url='/login/')
def localIndex(request):
    locals = Local.objects.all()
    context = {'locals': locals}
    return render(request, 'local/index.html', context)


@login_required(login_url='/login/')
def aseguramientoFind(request):
    aseguramientos = Aseguramiento.objects.filter(tipoAseguramiento=request.GET.get('tipoAseguramiento_id'))
    datos = [{
        'id': aseguramiento.pk,
        'nombre': aseguramiento.nombre
    }

        for aseguramiento in aseguramientos]

    # convertir eso en un json

    datos = json.dumps(datos)

    return HttpResponse(datos, content_type='application/json')


@login_required(login_url='/login/')
def denegarAceptarSolicitud(request):
    findSolicitud = Solicitud.objects.get(pk=request.GET.get('solicitud_id'))
    estado = Estado.objects.get(pk=request.GET.get('estado_id'))

    if estado.id == 2:
        solicitud = Solicitud.objects.filter(local=findSolicitud.local).filter(estado=estado).filter(
            Q(fechaInicio__gte=findSolicitud.fechaInicio, fechaFin__gte=findSolicitud.fechaFin) &
            (Q(horaInicio__gte=findSolicitud.horaInicio, horaFin__gt=findSolicitud.horaInicio) |
             Q(horaInicio__lte=findSolicitud.horaInicio, horaFin__gt=findSolicitud.horaInicio))
        ).exclude(id=findSolicitud.pk)
        if solicitud.count() == 0:
            solicitud = findSolicitud
            solicitud.estado = estado
            solicitud.save()
            # enviando correo al trabajador que pidio la reserva del local

            subject = 'Tu solicitud ha cambiado de estado'
            from_email = settings.EMAIL_FROM
            to = solicitud.solicitante.user.email
            text_content = 'Tienes una solicitud que ha cambiado de estado:\nhttps://sgrl.reduc.edu.cu/solicitud/' + str(
                solicitud.id) + '/show/'
            html_content = '<body>Tienes una solicitud que ha cambiado de estado:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
                solicitud.id) + '/show/> Solicitud cambiada de estado. </a>.</body>'
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return HttpResponse(200, content_type='application/json')
        else:
            return HttpResponseServerError(HttpResponse(400, content_type='application/json'))
    else:
        solicitud = findSolicitud
        solicitud.estado = estado
        solicitud.save()
        # enviando correo al trabajador que pidio la reserva del local

        subject = 'Tu solicitud ha cambiado de estado'
        from_email = settings.EMAIL_FROM
        to = solicitud.solicitante.user.email
        text_content = 'Tienes una solicitud que ha cambiado de estado:\nhttps://sgrl.reduc.edu.cu/solicitud/' + str(
            solicitud.id) + '/show/'
        html_content = '<body>Tienes una solicitud que ha cambiado de estado:  <a href=https://sgrl.reduc.edu.cu/solicitud/' + str(
            solicitud.id) + '/show/> Solicitud cambiada de estado. </a>.</body>'
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponse(200, content_type='application/json')


@login_required(login_url='/login/')
def aseguramientoDelete(request):
    datos = request.GET.getlist('aseguramientos[]')

    for dato in datos:
        aseguramientoSolicitud = AseguramientoSolicitud.objects.get(pk=dato)
        aseguramientoSolicitud.delete()
    return HttpResponse(200, content_type='application/json')


@login_required(login_url='/login/')
def actividadIndex(request):
    user = request.user
    existe = Trabajador.objects.filter(user=user).exists()
    if existe == False:
        return redirect('/perfil/')
    trabajador = Trabajador.objects.get(user=user)

    actividads = []
    if user.groups.filter(name='responsable_local').exists():
        locales = Local.objects.filter(responsables=trabajador)

        for local in locales:
            actividadLocal = Actividad.objects.filter(local=local)
            for actividad in actividadLocal:
                actividads.append(actividad)

    context = {'actividads': actividads}
    return render(request, 'actividad/index.html', context)


@login_required(login_url='/login/')
def actividadNew(request):
    user = request.user
    existe = Trabajador.objects.filter(user=user).exists()
    if existe == False:
        return redirect('/perfil/')
    trabajador = Trabajador.objects.get(user=user)
    if user.groups.filter(name='responsable_local').exists():
        locales = Local.objects.filter(responsables=trabajador)

    if request.method == 'POST':
        form = ActividadForm(locales, request.POST)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.save()
            messages.success(request, 'Actividad creada con exito.')
            return redirect('/actividad/index/')
        messages.error(request, 'La actividad no se pudo crear.')
    else:
        form = ActividadForm(locales)
    return render(request, 'actividad/new.html', {'form': form})


@login_required(login_url='/login/')
def actividadCreateAndNew(request):
    user = request.user
    existe = Trabajador.objects.filter(user=user).exists()
    if existe == False:
        return redirect('/perfil/')
    trabajador = Trabajador.objects.get(user=user)
    if user.groups.filter(name='responsable_local').exists():
        locales = Local.objects.filter(responsables=trabajador)
    if request.method == 'POST':
        form = ActividadForm(locales, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Actividad creada con exito.')
            return redirect('/actividad/new/')
        messages.error(request, 'La actividad no se pudo crear.')
    else:
        form = ActividadForm(locales)
    return render(request, 'actividad/new.html', {'form': form})


@login_required(login_url='/login/')
def actividadShow(request, actividad_id):
    actividad = Actividad.objects.get(pk=actividad_id)
    context = {'actividad': actividad}
    return render(request, 'actividad/show.html', context)


@login_required(login_url='/login/')
def actividadEdit(request, actividad_id):
    actividad = Actividad.objects.get(pk=actividad_id)
    user = request.user
    existe = Trabajador.objects.filter(user=user).exists()
    if existe == False:
        return redirect('/perfil/')
    trabajador = Trabajador.objects.get(user=user)
    if user.groups.filter(name='responsable_local').exists():
        locales = Local.objects.filter(responsables=trabajador)
    if request.method == 'POST':
        form = ActividadForm(locales, request.POST, instance=actividad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Se a editado dicha actividad.')
            return redirect('/actividad/index/')
        messages.error(request, 'No se ha podido editar la actividad.')
    else:
        form = ActividadForm(locales, instance=actividad)

    return render(request, 'actividad/edit.html', {'form': form, 'actividad': actividad})


@login_required(login_url='/login/')
def actividadDelete(request, actividad_id):
    actividad = Actividad.objects.get(pk=actividad_id)
    actividad.delete()
    messages.success(request, 'La actividad se elimino correctamente.')
    return redirect('/actividad/index/')


@login_required(login_url='/login/')
def actividadDeleteAll(request):
    datos = request.POST.getlist('select[]')
    for dato in datos:
        actividad = Actividad.objects.get(pk=dato)
        actividad.delete()
    if len(datos) == 1:
        messages.success(request, 'La actividad se elimino correctamente.')
    else:
        messages.success(request, 'Las actividades se eliminaron correctamente.')
    return redirect('/actividad/index/')
