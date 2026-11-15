from django.test import TestCase
from django.urls import reverse
from .models import Agendamento, Cliente


class BarbeariaMVPTests(TestCase):
    def test_index_carrega_corretamente(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Barbearia Oliveira")

    def test_fluxo_completo_agendamento(self):
        response = self.client.post(
            reverse("core:agendamento"),
            {
                "servico": "CORTE",
                "profissional": "OLIVEIRA",
                "horario": "09:00",
                "nome": "Carlos Silva",
                "telefone": "(11) 98888-7777",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_validacao_telefone_invalido(self):
        response = self.client.post(
            reverse("core:agendamento"),
            {
                "servico": "BARBA",
                "profissional": "LUCAS",
                "horario": "10:00",
                "nome": "Teste",
                "telefone": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Agendamento.objects.count(), 0)
