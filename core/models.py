from django.db import models


class Cliente(models.Model):
    nome = models.CharField("Nome Completo", max_length=100)
    telefone = models.CharField("Telefone / WhatsApp", max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nome} ({self.telefone})"


class Agendamento(models.Model):
    class ServicoChoices(models.TextChoices):
        CORTE = "CORTE", "Corte de Cabelo (R$ 40,00)"
        BARBA = "BARBA", "Barba Completa (R$ 30,00)"
        COMBO = "COMBO", "Corte + Barba (R$ 60,00)"

    class ProfissionalChoices(models.TextChoices):
        OLIVEIRA = "OLIVEIRA", "Seu Oliveira"
        LUCAS = "LUCAS", "Lucas"
        MARCOS = "MARCOS", "Marcos"

    class StatusChoices(models.TextChoices):
        AGENDADO = "AGENDADO", "Agendado"
        CONCLUIDO = "CONCLUIDO", "Concluído"
        CANCELADO = "CANCELADO", "Cancelado"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="agendamentos",
        verbose_name="Cliente",
    )
    servico = models.CharField(
        "Serviço",
        max_length=20,
        choices=ServicoChoices.choices,
    )
    profissional = models.CharField(
        "Profissional",
        max_length=20,
        choices=ProfissionalChoices.choices,
    )
    data_hora = models.DateTimeField("Data e Hora")
    status = models.CharField(
        "Status",
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.AGENDADO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["data_hora"]
        constraints = [
            models.UniqueConstraint(
                fields=["profissional", "data_hora"],
                condition=models.Q(status="AGENDADO"),
                name="unique_profissional_horario_ativo",
            )
        ]

    def __str__(self):
        return f"{self.cliente.nome} - {self.get_servico_display()} ({self.data_hora:%d/%m %H:%M})"
