from datetime import datetime, time
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import HORARIOS_PADRAO, ConfirmarAgendamentoForm, SelecaoInicialForm
from .models import Agendamento, Cliente


def index(request):
    """Tela 1: Seleção de serviço e profissional."""
    form = SelecaoInicialForm(request.GET or None)
    context = {
        "servicos": Agendamento.ServicoChoices.choices,
        "profissionais": Agendamento.ProfissionalChoices.choices,
        "form": form,
    }
    return render(request, "core/index.html", context)


def agendamento(request):
    """Tela 2: Exibição de horários livres no dia e dados do cliente."""
    servico = request.GET.get("servico")
    profissional = request.GET.get("profissional")

    validacao_inicial = SelecaoInicialForm({"servico": servico, "profissional": profissional})
    if not validacao_inicial.is_valid():
        messages.error(request, "Por favor, escolha o serviço e o profissional primeiro.")
        return redirect("core:index")

    data_str = request.GET.get("data")
    hoje = timezone.localdate()
    try:
        data_escolhida = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else hoje
        if data_escolhida < hoje:
            data_escolhida = hoje
    except ValueError:
        data_escolhida = hoje

    agendados_no_dia = Agendamento.objects.filter(
        profissional=profissional,
        data_hora__date=data_escolhida,
        status=Agendamento.StatusChoices.AGENDADO,
    )
    horarios_ocupados = {
        timezone.localtime(ag.data_hora).strftime("%H:%M") for ag in agendados_no_dia
    }

    horarios_livres = [h for h in HORARIOS_PADRAO if h not in horarios_ocupados]

    if request.method == "POST":
        form = ConfirmarAgendamentoForm(request.POST)
        if form.is_valid():
            horario_str = form.cleaned_data["horario"]

            if horario_str not in horarios_livres:
                form.add_error("horario", "Este horário acabou de ser preenchido. Escolha outro.")
            else:
                hora, minuto = map(int, horario_str.split(":"))
                data_hora_naive = datetime.combine(data_escolhida, time(hora, minuto))
                data_hora_aware = timezone.make_aware(data_hora_naive)

                cliente, _ = Cliente.objects.update_or_create(
                    telefone=form.cleaned_data["telefone"],
                    defaults={"nome": form.cleaned_data["nome"]},
                )

                novo_agendamento = Agendamento.objects.create(
                    cliente=cliente,
                    servico=servico,
                    profissional=profissional,
                    data_hora=data_hora_aware,
                )
                return redirect("core:sucesso", agendamento_id=novo_agendamento.id)
    else:
        form = ConfirmarAgendamentoForm()

    context = {
        "form": form,
        "servico_cod": servico,
        "servico_nome": dict(Agendamento.ServicoChoices.choices).get(servico),
        "profissional_cod": profissional,
        "profissional_nome": dict(Agendamento.ProfissionalChoices.choices).get(profissional),
        "data_escolhida": data_escolhida,
        "horarios_livres": horarios_livres,
    }
    return render(request, "core/agendamento.html", context)


def sucesso(request, agendamento_id):
    """Tela 3: Confirmação clara do agendamento."""
    agendamento_obj = get_object_or_404(Agendamento, id=agendamento_id)
    return render(request, "core/sucesso.html", {"agendamento": agendamento_obj})


@login_required
def painel_barbeiro(request):
    """Tela Admin: Rota protegida com os agendamentos do dia."""
    data_str = request.GET.get("data")
    hoje = timezone.localdate()
    try:
        data_filtro = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else hoje
    except ValueError:
        data_filtro = hoje

    if request.method == "POST":
        agendamento_id = request.POST.get("agendamento_id")
        novo_status = request.POST.get("novo_status")
        if novo_status in Agendamento.StatusChoices.values:
            Agendamento.objects.filter(id=agendamento_id).update(status=novo_status)
            messages.success(request, "Status atualizado com sucesso!")
        return redirect(f"{request.path}?data={data_filtro:%Y-%m-%d}")

    agendamentos = Agendamento.objects.select_related("cliente").filter(
        data_hora__date=data_filtro
    ).order_by("data_hora")

    return render(request, "core/painel.html", {
        "agendamentos": agendamentos,
        "data_filtro": data_filtro,
    })
