from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='default/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('calendario/', views.calendario, name='calendario'),
    path('perfil/', views.trabajadorEdit, name='perfil'),
    path('perfil/remove/', views.trabajadorDelete, name='perfil_delete'),
    path('solicitud/index/', views.solicitudIndex, name='solicitud_index'),
    path('solicitud/new/', views.solicitudNew, name='solicitud_new'),
    path('solicitud/<int:solicitud_id>/show/', views.solicitudShow, name='solicitud_show'),
    path('solicitud/create_and_new/', views.solicitudCreateAndNew, name='solicitud_create_and_new'),
    path('solicitud/<int:solicitud_id>/edit', views.solicitudEdit, name='solicitud_edit'),
    path('solicitud/<int:solicitud_id>/delete', views.solicitudDelete, name='solicitud_delete'),
    path('solicitud/<int:solicitud_id>/aceptar', views.solicitudAceptar, name='solicitud_aceptar'),
    path('solicitud/<int:solicitud_id>/denegar', views.solicitudDenegar, name='solicitud_denegar'),
    path('solicitud/delete/all', views.solicitudDeleteAll, name='solicitud_delete_all'),
    path('solicitud/aceptar/all', views.solicitudAceptarAll, name='solicitud_aceptar_all'),
    path('solicitud/denegar/all', views.solicitudDenegarAll, name='solicitud_denegar_all'),
    path('solicitud/<int:local_id>/new', views.solicitudNueva, name='solicitud_nueva'),
    path('aseguramiento/solicitud/<int:solicitud_id>/new/', views.aseguramientoSolicitudNew, name='aseguramiento_solicitud_new'),
    path('aseguramiento/solicitud/<int:solicitud_id>/create_and_new/', views.aseguramientoSolicitudCreateAndNew, name='aseguramiento_solicitud_create_and_new'),
    path('aseguramiento/solicitud/<int:aseguramientoSolicitud_id>/edit/', views.aseguramientoSolicitudEdit, name='aseguramiento_solicitud_edit'),
    path('aseguramiento/solicitud/<int:aseguramientoSolicitud_id>/delete', views.aseguramientoSolicitudDelete, name='aseguramiento_solicitud_delete'),
    path('aseguramiento/find/', views.aseguramientoFind, name='aseguramiento_find'),
    path('aseguramiento/delete/', views.aseguramientoDelete, name='aseguramiento_delete'),
    path('local/index/', views.localIndex, name='local_index'),
    path('proxy/', views.proxy, name='proxy'),
    path('solicitud/cambiar/estado', views.denegarAceptarSolicitud, name='denegar_aceptar_solicitud'),
    path('actividad/index/', views.actividadIndex, name='actividad_index'),
    path('actividad/new/', views.actividadNew, name='actividad_new'),
    path('actividad/<int:actividad_id>/show/', views.actividadShow, name='actividad_show'),
    path('actividad/create_and_new/', views.actividadCreateAndNew, name='actividad_create_and_new'),
    path('actividad/<int:actividad_id>/edit', views.actividadEdit, name='actividad_edit'),
    path('actividad/<int:actividad_id>/delete', views.actividadDelete, name='actividad_delete'),
    path('actividad/delete/all', views.actividadDeleteAll, name='actividad_delete_all'),
]
