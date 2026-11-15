from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("agendar/", views.agendamento, name="agendamento"),
    path("sucesso/<int:agendamento_id>/", views.sucesso, name="sucesso"),
    path("barbeiro/", views.painel_barbeiro, name="painel_barbeiro"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
