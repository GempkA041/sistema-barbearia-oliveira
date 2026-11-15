import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

# Garante que as tabelas do banco de dados estejam criadas ao iniciar o servidor no Render
try:
    from django.core.management import call_command
    call_command("migrate", interactive=False, verbosity=1)
except Exception as exc:
    print(f"[AVISO] Erro ao executar migrate automático no startup: {exc}")
