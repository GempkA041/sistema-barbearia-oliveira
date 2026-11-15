from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cliente",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=100, verbose_name="Nome Completo")),
                (
                    "telefone",
                    models.CharField(max_length=20, verbose_name="Telefone / WhatsApp"),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Cliente",
                "verbose_name_plural": "Clientes",
            },
        ),
        migrations.CreateModel(
            name="Agendamento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "servico",
                    models.CharField(
                        choices=[
                            ("CORTE", "Corte de Cabelo (R$ 40,00)"),
                            ("BARBA", "Barba Completa (R$ 30,00)"),
                            ("COMBO", "Corte + Barba (R$ 60,00)"),
                        ],
                        max_length=20,
                        verbose_name="Serviço",
                    ),
                ),
                (
                    "profissional",
                    models.CharField(
                        choices=[
                            ("OLIVEIRA", "Seu Oliveira"),
                            ("LUCAS", "Lucas"),
                            ("MARCOS", "Marcos"),
                        ],
                        max_length=20,
                        verbose_name="Profissional",
                    ),
                ),
                ("data_hora", models.DateTimeField(verbose_name="Data e Hora")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("AGENDADO", "Agendado"),
                            ("CONCLUIDO", "Concluído"),
                            ("CANCELADO", "Cancelado"),
                        ],
                        default="AGENDADO",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="agendamentos",
                        to="core.cliente",
                        verbose_name="Cliente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Agendamento",
                "verbose_name_plural": "Agendamentos",
                "ordering": ["data_hora"],
            },
        ),
        migrations.AddConstraint(
            model_name="agendamento",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "AGENDADO")),
                fields=("profissional", "data_hora"),
                name="unique_profissional_horario_ativo",
            ),
        ),
    ]
