from datetime import datetime, time
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    HORARIOS_PADRAO,
    ClienteForm,
    ConfirmarAgendamentoForm,
    SelecaoInicialForm,
)
from .models import Agendamento, Cliente


SERVICOS_DETALHES = [
    {
        "codigo": "CORTE",
        "titulo": "Corte de Cabelo",
        "descricao": "Corte social, degradê ou navalhado com acabamento na toalha quente.",
        "preco": "R$ 40,00",
        "duracao": "40 min",
        "icone": "✂️",
    },
    {
        "codigo": "BARBA",
        "titulo": "Barba Completa",
        "descricao": "Modelagem de barba com toalha quente, óleo hidratante e navalha.",
        "preco": "R$ 30,00",
        "duracao": "30 min",
        "icone": "🪒",
    },
    {
        "codigo": "COMBO",
        "titulo": "Combo Corte + Barba",
        "descricao": "Experiência completa de visagismo: cabelo, barba e finalização premium.",
        "preco": "R$ 60,00",
        "duracao": "60 min",
        "icone": "💈",
    },
]

PROFISSIONAIS_DETALHES = [
    {
        "codigo": "OLIVEIRA",
        "nome": "Seu Oliveira",
        "especialidade": "Mestre Barbeiro • Clássicos & Barba Tradicional",
        "inicial": "O",
    },
    {
        "codigo": "LUCAS",
        "nome": "Lucas",
        "especialidade": "Especialista em Fade / Degradê & Cortes Modernos",
        "inicial": "L",
    },
    {
        "codigo": "MARCOS",
        "nome": "Marcos",
        "especialidade": "Visagismo, Barboterapia & Acabamento na Navalha",
        "inicial": "M",
    },
]


def index(request):
    """Tela 1: Painel inicial + Seleção rápida de Serviço e Profissional."""
    hoje = timezone.localdate()
    todos = Agendamento.objects.select_related("cliente").all()

    total_agendamentos = todos.count()
    agendados_ativos = todos.filter(status="AGENDADO").count()
    concluidos = todos.filter(status="CONCLUIDO").count()
    hoje_count = todos.filter(data_hora__date=hoje, status="AGENDADO").count()

    recentes = todos.order_by("-data_hora")[:5]

    context = {
        "servicos": Agendamento.ServicoChoices.choices,
        "profissionais": Agendamento.ProfissionalChoices.choices,
        "servicos_detalhes": SERVICOS_DETALHES,
        "profissionais_detalhes": PROFISSIONAIS_DETALHES,
        "stats": {
            "total": total_agendamentos,
            "agendados": agendados_ativos,
            "hoje": hoje_count,
            "concluidos": concluidos,
        },
        "recentes": recentes,
    }
    return render(request, "core/index.html", context)


def agendamento(request):
    """Tela 2: Exibição de horários livres no dia, dados do cliente e confirmação."""
    servico = request.GET.get("servico") or request.POST.get("servico") or "CORTE"
    profissional = request.GET.get("profissional") or request.POST.get("profissional") or "OLIVEIRA"

    validacao_inicial = SelecaoInicialForm({"servico": servico, "profissional": profissional})
    if not validacao_inicial.is_valid():
        servico = "CORTE"
        profissional = "OLIVEIRA"

    data_str = request.GET.get("data") or request.POST.get("data")
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
    grade_horarios = [
        {"hora": h, "livre": h not in horarios_ocupados} for h in HORARIOS_PADRAO
    ]

    if request.method == "POST":
        form = ConfirmarAgendamentoForm(request.POST)
        if form.is_valid():
            horario_str = form.cleaned_data["horario"]

            if horario_str not in horarios_livres:
                form.add_error("horario", "Este horário acabou de ser reservado. Escolha outro horário livre.")
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
                messages.success(request, "Marcação confirmada com sucesso!")
                return redirect("core:sucesso", agendamento_id=novo_agendamento.id)
    else:
        cliente_id = request.GET.get("cliente_id")
        initial_data = {}
        if cliente_id and cliente_id.isdigit():
            cli = Cliente.objects.filter(id=int(cliente_id)).first()
            if cli:
                initial_data = {"nome": cli.nome, "telefone": cli.telefone}
        form = ConfirmarAgendamentoForm(initial=initial_data)

    context = {
        "form": form,
        "servicos": Agendamento.ServicoChoices.choices,
        "profissionais": Agendamento.ProfissionalChoices.choices,
        "servico_cod": servico,
        "servico_nome": dict(Agendamento.ServicoChoices.choices).get(servico),
        "profissional_cod": profissional,
        "profissional_nome": dict(Agendamento.ProfissionalChoices.choices).get(profissional),
        "data_escolhida": data_escolhida,
        "hoje": hoje,
        "horarios_livres": horarios_livres,
        "grade_horarios": grade_horarios,
    }
    return render(request, "core/agendamento.html", context)


def sucesso(request, agendamento_id):
    """Tela 3: Confirmação clara do agendamento."""
    agendamento_obj = get_object_or_404(Agendamento.objects.select_related("cliente"), id=agendamento_id)
    return render(request, "core/sucesso.html", {"agendamento": agendamento_obj})


def painel_barbeiro(request):
    """Tela Admin / Gestão da Agenda da Barbearia."""
    busca = request.GET.get("q", "").strip()
    status_filtro = request.GET.get("status", "").strip()
    profissional_filtro = request.GET.get("profissional", "").strip()
    data_str = request.GET.get("data", "").strip()

    if request.method == "POST":
        agendamento_id = request.POST.get("agendamento_id")
        novo_status = request.POST.get("novo_status")
        if novo_status in Agendamento.StatusChoices.values:
            updated = Agendamento.objects.filter(id=agendamento_id).update(status=novo_status)
            if updated:
                messages.success(request, "Status do agendamento atualizado com sucesso!")
        return redirect("core:painel_barbeiro")

    agendamentos = Agendamento.objects.select_related("cliente").all()

    if busca:
        agendamentos = agendamentos.filter(
            Q(cliente__nome__icontains=busca) | Q(cliente__telefone__icontains=busca)
        )
    if status_filtro in Agendamento.StatusChoices.values:
        agendamentos = agendamentos.filter(status=status_filtro)
    if profissional_filtro in Agendamento.ProfissionalChoices.values:
        agendamentos = agendamentos.filter(profissional=profissional_filtro)
    if data_str:
        try:
            data_parsed = datetime.strptime(data_str, "%Y-%m-%d").date()
            agendamentos = agendamentos.filter(data_hora__date=data_parsed)
        except ValueError:
            pass

    agendamentos = agendamentos.order_by("data_hora")

    return render(request, "core/painel.html", {
        "agendamentos": agendamentos,
        "statuses": Agendamento.StatusChoices.choices,
        "profissionais": Agendamento.ProfissionalChoices.choices,
        "q": busca,
        "status_filtro": status_filtro,
        "profissional_filtro": profissional_filtro,
        "data_filtro": data_str,
    })


def clientes(request):
    """Tela de Cadastro e Listagem de Clientes."""
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            Cliente.objects.update_or_create(
                telefone=form.cleaned_data["telefone"],
                defaults={"nome": form.cleaned_data["nome"]},
            )
            messages.success(request, "Cliente cadastrado com sucesso!")
            return redirect("core:clientes")
    else:
        form = ClienteForm()

    lista_clientes = Cliente.objects.annotate(
        total_agendamentos=Count("agendamentos")
    ).order_by("nome")

    return render(request, "core/clientes.html", {
        "form": form,
        "clientes": lista_clientes,
    })
