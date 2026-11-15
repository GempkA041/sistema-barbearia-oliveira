from django.contrib import admin
from .models import Agendamento, Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "criado_em")
    search_fields = ("nome", "telefone")


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ("cliente", "servico", "profissional", "data_hora", "status")
    list_filter = ("status", "profissional", "servico", "data_hora")
    search_fields = ("cliente__nome", "cliente__telefone")
