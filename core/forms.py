import re
from django import forms
from django.utils.html import strip_tags
from .models import Agendamento


HORARIOS_PADRAO = [
    "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
]


class SelecaoInicialForm(forms.Form):
    servico = forms.ChoiceField(
        choices=Agendamento.ServicoChoices.choices,
        label="Escolha o Serviço",
        error_messages={"required": "Selecione um serviço."},
    )
    profissional = forms.ChoiceField(
        choices=Agendamento.ProfissionalChoices.choices,
        label="Escolha o Profissional",
        error_messages={"required": "Selecione um profissional."},
    )


class ConfirmarAgendamentoForm(forms.Form):
    nome = forms.CharField(
        label="Seu Nome Completo",
        max_length=100,
        min_length=3,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: João da Silva",
            "autocomplete": "name",
        }),
    )
    telefone = forms.CharField(
        label="Seu WhatsApp / Telefone (com DDD)",
        max_length=20,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: (11) 99999-8888",
            "type": "tel",
            "autocomplete": "tel",
        }),
    )
    horario = forms.ChoiceField(
        label="Horário Disponível",
        choices=[(h, h) for h in HORARIOS_PADRAO],
        error_messages={"required": "Por favor, selecione um horário livre."},
    )

    def clean_nome(self):
        nome = strip_tags(self.cleaned_data.get("nome", "")).strip()
        if len(nome) < 3:
            raise forms.ValidationError("Informe um nome válido com pelo menos 3 letras.")
        return nome

    def clean_telefone(self):
        telefone = strip_tags(self.cleaned_data.get("telefone", "")).strip()
        apenas_digitos = re.sub(r"\D", "", telefone)
        if len(apenas_digitos) not in (10, 11):
            raise forms.ValidationError("Digite um telefone válido com DDD (10 ou 11 números).")
        return telefone
